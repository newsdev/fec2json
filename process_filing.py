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
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CSV_FILE_DIRECTORY = '{}/fec-csv-sources'.format(PROJECT_ROOT)

def process_electronic_filing(path):
    filing_dict = {}
    with open(path, 'r') as f:
        reader = csv.reader(f)
        fec_header = next(reader)
        fec_version_number = fec_header[2]

        #these fields come from the first row of the fec file
        filing_dict['record_type'] = fec_header[0]
        filing_dict['electronic_filing_type'] = fec_header[1]
        filing_dict['fec_version_number'] = fec_header[2]
        filing_dict['software_name'] = fec_header[3]
        filing_dict['software_version'] = fec_header[4]
        filing_dict['report_id'] = fec_header[5]
        filing_dict['report_type'] = fec_header[6]
        try:
            filing_dict['header_comment'] = fec_header[7]
        except IndexError:
            filing_dict['header_comment'] = None
            print("this filing doesn't have a header comment")
        
        summary_row = next(reader)
        processed_summary = process_summary_row(summary_row, fec_version_number)
        assert processed_summary, "Summary could not be processed"
        filing_dict.update(processed_summary)
        
        filing_dict['itemizations'] = {}
        for line in reader:
            form_type = get_itemization_type(line[0])
            #print(form_type)
            if form_type not in filing_dict['itemizations']:
                filing_dict['itemizations'][form_type] = []
            itemization = process_itemization_line(line, fec_version_number)
            if not itemization:
                print('itemization failed, skipping')
                continue
            filing_dict['itemizations'][form_type].append(itemization)


        return filing_dict

def process_summary_row(summary_row, fec_version_number):
    #processes the second row of the filing, which is the form summary/topline row
    form_type = summary_row[0]
    if form_type.endswith('N'):
        amendment = False
        form_type = form_type.rstrip('N')
    elif form_type.endswith('A'):
        amendment = True
        form_type = form_type.rstrip('A')

    processed_fields = process_line(summary_row, fec_version_number, form_type)
    if processed_fields:
        processed_fields['amendment'] = amendment
        processed_fields['form'] = form_type #this has the N or A removed

        return(processed_fields)

def process_itemization_line(line, fec_version_number):
    #processes a single itemization row
    form_type = get_itemization_type(line[0])
    return process_line(line, fec_version_number, form_type)


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
        print('could not find headers for form type {}'.format(form_type))
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
            processed_fields[k] = line[v-1]
        except IndexError:
            print(header_dict)
            print(line)

    return(processed_fields)

def get_itemization_type(line_type):
    #figure out the itemization type based on the FEC description of the line
    if line_type == "TEXT":
        return "TEXT"
    if line_type.startswith('SA3L'):
        return "SchA3L"
    if line_type.startswith('SC1'):
        return "SchC1"
    if line_type.startswith('SC2'):
        return "SchC2"
    return "Sch"+line_type[1]#this is probably going to need to be more complex

def write_file(outpath, content):
    #eventually we'll probably want to make this write to S3 or google
    with open(outpath, 'w') as f:
        f.write(json.dumps(content, indent=2))

def main():
    #do some argparse stuff
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to the fec file we want to load')
    parser.add_argument('--fecfile', action='store_true', default=False, help='indicates we\'re using a .fec file instead of the fec\'s .csv file. .csv is default and recommended for messy whitespace reasons')
    args = parser.parse_args()

    assert not args.fecfile, "parsing for .fec file not yet implemented, use .csv file"
    content = process_electronic_filing(args.path)
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