import csv
import sys
import os
import ujson as json
import datetime
import argparse

"""
this will be a dictionary of the sources we've loaded.
since fec2json only deals with one form at a time it'll only
be one version, but to prevent re-loading each sked's headers
over and over, we'll cache the ones we've already loaded
in the FEC_SOURCES global
"""
FEC_SOURCES = {}
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
CSV_FILE_DIRECTORY = '{}/fec-csv-sources'.format(PROJECT_ROOT)

def get_delimiter(line):
    if len(line.split('\034')) > 1:
        return '\034'
    elif len(line.split(',')) > 1:
        return ','
    raise Exception("Cannot parse first line")

def process_electronic_filing(path, filing_id=None, dump_full=True):
    #if dump_full is true, you'll get the whole filing, and "itemizations"
    #will include all itemizations grouped by category
    #otherwise "itemizations" will be in iterator
    filing_dict = {}
    with open(path, 'r', errors='replace') as f:
        delimiter = get_delimiter(next(f))
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)
        fec_header = next(reader)
        fec_version_number = fec_header[2].strip()

        #these fields come from the first row of the fec file
        filing_dict['record_type'] = list_get(fec_header, 0)
        filing_dict['electronic_filing_type'] = list_get(fec_header, 1)
        filing_dict['fec_version_number'] = list_get(fec_header, 2)
        filing_dict['software_name'] = list_get(fec_header, 3)
        filing_dict['software_version'] = list_get(fec_header, 4)
        filing_dict['report_id'] = list_get(fec_header, 5)
        filing_dict['report_type'] = list_get(fec_header, 6)
        filing_dict['header_comment'] = list_get(fec_header, 7)
        
        summary_row = next(reader)
        processed_summary = process_summary_row(summary_row, fec_version_number)
        assert processed_summary, "Summary could not be processed"
        filing_dict.update(processed_summary)

        if filing_dict['amendment']:
            filing_dict['amends_filing'] = filing_dict['report_id'].replace('FEC-', '')
        else:
            filing_dict['amends_filing'] = None

        
        
        itemizations = itemization_iterator(path, filing_id, fec_version_number)
        if dump_full:
            filing_dict['itemizations'] = {}
            for itemization in itemizations:
                form_type = get_itemization_type(itemization.get('form_type'))
                if not form_type:
                    form_type = get_itemization_type(itemization.get('rec_type'))
                    if not form_type:
                        continue
                if form_type not in filing_dict['itemizations']:
                    filing_dict['itemizations'][form_type] = []
                filing_dict['itemizations'][form_type].append(itemization)
        else:
            filing_dict['itemizations'] = itemizations

        return filing_dict

def itemization_iterator(path, filing_id, fec_version_number):
    with open(path, 'r', errors='replace') as f:
        delimiter = get_delimiter(next(f))
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)
        fec_header = next(reader)
        summary_row = next(reader)
        for line in reader:
            if line:
                form_type = get_itemization_type(line[0])
                if not form_type:
                    print('bad itemization line')
                    continue
                itemization = process_itemization_line(line, fec_version_number)
                if not itemization:
                    print('itemization failed, skipping')
                    continue

                if not filing_id:
                    try:
                        filing_id = path.strip('/').split('/')[-1].split('.')[0]
                    except:
                        filing_id = None
            itemization['filing_id'] = filing_id
            yield itemization

def process_summary_row(summary_row, fec_version_number):
    #processes the second row of the filing, which is the form summary/topline row
    form_type = summary_row[0]
    if form_type.endswith('N'):
        amendment = False
        form = form_type.rstrip('N')
    elif form_type.endswith('A'):
        amendment = True
        form = form_type.rstrip('A')

    processed_fields = process_line(summary_row, fec_version_number, form)
    if processed_fields:
        processed_fields['amendment'] = amendment
        processed_fields['form'] = form
        return(processed_fields)

def process_itemization_line(line, fec_version_number):
    #processes a single itemization row
    form_type = get_itemization_type(line[0])
    if form_type:
        return process_line(line, fec_version_number, form_type)
    return None

def get_header_columns(fec_version_number, form_type):
    #if we haven't seen this form before, pull the correct version out of fec sources
    #note that these files were written to be used with regex
    #but this was fast and easy so voila.
    #(also you should see the old regex code!)
    #but I'll comment this carefully.

    #open the fec source for the relevant form
    try:
        f = open('{}/{}.csv'.format(CSV_FILE_DIRECTORY, form_type), 'r')
    except FileNotFoundError:
        print('could not find headers for form type {} in {}'.format(form_type, CSV_FILE_DIRECTORY))
        raise

    csv_headers = csv.reader(f)
    versions = next(csv_headers) #this top row lists the fec software versions
    i = 0
    while i < len(versions):
        version_list = versions[i].replace("^", "").split("|") #split the versions by pipe
        if fec_version_number in version_list:
            #if we find the version we're looking for, set the column number and get our of this loop
            col_number = i
            break
        i += 1
    else:
        #if we do not break out of the loop, we end up here.
        #we should probably write better errors
        assert False, "unsupported version of fec file"
        
    header_to_col = {}
    #this is going to be a dictionary from header name to column number
    for line in csv_headers:
        try:
            value_column = int(line[col_number])
        except ValueError:
            #this takes care of the fact that fields for previous or new FEC versions
            #are in there with no number for the current version and isn't a concern
            continue                
        header_to_col[line[0]] = value_column
    
    f.close() #let's get out of that file
    
    #add this dictionary to the global FEC_SOURCES dict so we only have to do this once per line type
    FEC_SOURCES[form_type] = header_to_col
    

def process_line(line, fec_version_number, form_type):
    #for any line, find the headers for the form type and return the line as a header:value dict
    if form_type not in FEC_SOURCES:
        try:
            get_header_columns(fec_version_number, form_type)
        except FileNotFoundError:
            return
        

    header_dict = FEC_SOURCES[form_type]
    processed_fields = {}
    for k, v in header_dict.items():
        try:
            processed_fields[k] = list_get(line, v-1) or None #turns blanks into nones
        except IndexError:
            print(header_dict)
            print(line)

    return(processed_fields)

def get_itemization_type(line_type):
    if not line_type:
        return None
    #figure out the itemization type based on the FEC description of the line
    if line_type == "TEXT":
        return "TEXT"
    if line_type.startswith('SA3L'):
        return "SchA3L"
    if line_type.startswith('SC1'):
        return "SchC1"
    if line_type.startswith('SC2'):
        return "SchC2"
    if line_type.startswith('H'):
        return line_type
    if line_type.startswith('F'):
        return line_type
    return "Sch"+line_type[1]

def list_get(l, i, default=None):
    #like dict.get, but for a list - returns the item or a default other thing if it doesn't exist
    return l[i] if i < len(l) else default


def write_file(outpath, content):
    #eventually we'll probably want to make this write to S3 or google
    with open(outpath, 'w') as f:
        f.write(json.dumps(content, indent=2))

def main():
    #do some argparse stuff
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to the fec file we want to load')
    parser.add_argument('--filing_id', help='if not available, assume that filing id is the filename minus the extension.')
    args = parser.parse_args()

    content = process_electronic_filing(args.path, args.filing_id)
    sys.stdout.write(json.dumps(content))

if __name__=='__main__':
    main()

"""
start_time = datetime.datetime.now()

filing_dict = process_electronic_filing('test_csvs/1205803.csv')
write_file('test_csvs/output_test.json', filing_dict)

end_time = datetime.datetime.now()
time_diff = end_time-start_time
print("processing took {} seconds".format(time_diff.seconds))
"""