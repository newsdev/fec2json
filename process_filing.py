import csv
import ujson as json
import datetime

"""
this will be a dictionary of the sources we've loaded.
since fec2json only deals with one form at a time it'll only
be one version, but to prevent re-loading each sked's headers
over and over, we'll cache the ones we've already loaded
in the FEC_SOURCES global
"""
FEC_SOURCES = {}

def process_electronic_filing(path):
    filing_dict = {}
    with open(path, 'r') as f:
        reader = csv.reader(f)
        fec_header = next(reader)
        fec_version_number = fec_header[2]
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
            print("this filing doesn't have a header comment")
        summary_row = next(reader)

        filing_dict.update(process_form_header(summary_row, fec_version_number))

        filing_dict['itemizations'] = {}
        for line in reader:
            form_type = get_itemization_type(line[0])
            #print(form_type)
            if form_type not in filing_dict['itemizations']:
                filing_dict['itemizations'][form_type] = []
            filing_dict['itemizations'][form_type].append(process_itemization_line(line, fec_version_number))


        return filing_dict

def process_form_header(summary_row, fec_version_number):
    form_type = summary_row[0]
    if form_type.endswith('N'):
        amendment = False
        form_type = form_type.rstrip('N')
    elif form_type.endswith('A'):
        amendment = True
        form_type = form_type.rstrip('A')

    processed_fields = process_line(summary_row, fec_version_number, form_type)
    processed_fields['amendment'] = amendment
    processed_fields['form'] = form_type #this has the N or A removed

    return(processed_fields)

def process_itemization_line(line, fec_version_number):
    form_type = get_itemization_type(line[0])
    return process_line(line, fec_version_number, form_type)


def get_header_columns(f, fec_version_number, form_type):
    csv_headers = csv.reader(f)
    versions = next(csv_headers)
    i = 0
    while i < len(versions):
        version_list = versions[i].replace("^", "").split("|")
        if fec_version_number in version_list:
            col_number = i
            break
        i += 1
    col_to_header = {}
    for line in csv_headers:
        try:
            value_column = int(line[col_number])
        except ValueError:
            continue                
        col_to_header[line[0]] = value_column
    
    FEC_SOURCES[form_type] = col_to_header

def process_line(line, fec_version_number, form_type):
    if form_type not in FEC_SOURCES:
        try:
            f = open('fec-csv-sources/{}.csv'.format(form_type), 'r')
        except FileNotFoundError:
            print('could not find headers for form type {}'.format(form_type))
            return

        get_header_columns(f, fec_version_number, form_type)
        f.close()

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

start_time = datetime.datetime.now()

filing_dict = process_electronic_filing('test_csvs/1205803.csv')
write_file('test_csvs/output_test.json', filing_dict)

end_time = datetime.datetime.now()
time_diff = end_time-start_time
print("processing took {} seconds".format(time_diff.seconds))