import csv

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
        filing_dict['header_comment'] = fec_header[7]
        form_header = next(reader)


        process_form_header(form_header, fec_version_number)

def process_form_header(form_header, fec_version_number):
    form_type = form_header[0]
    if form_type.endswith('N'):
        amended = False
        form_type = form_type.rstrip('N')
    elif form_type.endswith('A'):
        amended = True
        form_type = form_type.rstrip('A')
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
        processed_fields[k] = form_header[v-1]

    print(processed_fields)




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



process_electronic_filing('1205803.csv')