# fec2json
turn fec files into json

work in progress, not yet trustworthy


The purpose of this library is to turn files from the fec format into json.

## Running
Requires python3.x. To install dependencies, `pip install -r requirements.txt`. We recommend you do that in a virtual enviromnet.

### CLI:
`fec2json --path path/to/filing`
Takes the following optional commandline arguments
* `--fecfile` if you have .fec files instead of .csv files (no argument needed, this stores a boolean, we assume it's csv if not specified)
* `--filing_id` to specify the filing id. If not specified, we assume it is the filename minus the directory path and extension.


The json will have the following keys:

#### from the first line of the fec file:
* record_type
* electronic_filing_type
* fec_version_number
* software_name
* software_version
* report_id
* report_type
* header_comment
* amends_filing (pulled from report_id)

#### from the second line of the fec file
* amendment (whether the file is amended)
* form (the form type minus the `N` or `A`)
* remaining fields depend on the form type and come from the relevant [fec csv source file](https://github.com/newsdev/fec-csv-sources)


#### from the itemizations
* itemizations, an object which includes keys for each sked type
  * each of those keys points to a list of itemization objects of the relevant type. The keys for those innermost objects are determined by the relevant [fec csv source file](https://github.com/newsdev/fec-csv-sources)
  * each itemization also includes filing_id of the filing. The filing ID. The filing ID can be provided as a command line argument when running in command line mode. If it is not provided, we assume the filing's path is of the format `path/to/filing/filing_id.ext`.

For example, a filing might look like this:

```
{
  "record_type":"HDR",
  "electronic_filing_type":"FEC",
  "fec_version_number":"8.2",
  "software_name":"NGP",
  "software_version":"8",
  "report_id":"",
  "report_type":"",
  "header_comment":"",
  "form_type":"F3N",
  "filer_committee_id_number":"C00654178",
  "committee_name":"Sara Dady for Congress",
  "change_of_address":"",
  "street_1":"PO Box 7164",
  "street_2":"",
  "city":"Rockford",
  "state":"IL",
  "zip":"61126",
  "report_code":"YE",
  "election_code":"",
  "election_date":"",
  "election_state":"IL",
  "election_district":"16",
  "state_of_election":"",
  "coverage_from_date":"20171001",
  "coverage_through_date":"20171231",
  "treasurer_last_name":"Lashock",
  "treasurer_first_name":"Gwen",
  "treasurer_middle_name":"",
  "treasurer_prefix":"",
  "treasurer_suffix":"",
  "date_signed":"20180131",
  "col_a_total_contributions_no_loans":"54485.57",
  "col_a_total_contributions_refunds":"255.00",
  "col_a_net_contributions":"54230.57",
  "col_a_total_operating_expenditures":"72966.66",
  "col_a_total_offset_to_operating_expenditures":"0.00",
  "col_a_net_operating_expenditures":"72966.66",
  "col_a_cash_on_hand_close_of_period":"23164.12",
  "col_a_debts_to":"0.00",
  "col_a_debts_by":"0.00",
  "col_a_individual_contributions_itemized":"30420.00",
  "col_a_individual_contributions_unitemized":"22850.57",
  "col_a_total_individual_contributions":"53270.57",
  "col_a_political_party_contributions":"0.00",
  "col_a_pac_contributions":"1100.00",
  "col_a_candidate_contributions":"115.00",
  "col_a_total_contributions":"54485.57",
  "col_a_transfers_from_authorized":"0.00",
  "col_a_candidate_loans":"0.00",
  "col_a_other_loans":"0.00",
  "col_a_total_loans":"0.00",
  "col_a_offset_to_operating_expenditures":"0.00",
  "col_a_other_receipts":"0.00",
  "col_a_total_receipts":"54485.57",
  "col_a_operating_expenditures":"72966.66",
  "col_a_transfers_to_authorized":"0.00",
  "col_a_candidate_loan_repayments":"0.00",
  "col_a_other_loan_repayments":"0.00",
  "col_a_total_loan_repayments":"0.00",
  "col_a_refunds_to_individuals":"255.00",
  "col_a_refunds_to_party_committees":"54485.57",
  "col_a_refunds_to_other_committees":"96385.78",
  "col_a_total_refunds":"255.00",
  "col_a_other_disbursements":"0.00",
  "col_a_total_disbursements":"73221.66",
  "col_a_cash_on_hand_beginning_period":"41900.21",
  "col_a_total_disbursements_period":"73221.66",
  "col_b_total_contributions_no_loans":"114759.59",
  "col_b_total_contributions_refunds":"1055.00",
  "col_b_net_contributions":"113704.59",
  "col_b_total_operating_expenditures":"88530.47",
  "col_b_total_offset_to_operating_expenditures":"0.00",
  "col_b_net_operating_expenditures":"88530.47",
  "col_b_individual_contributions_itemized":"73548.96",
  "col_b_individual_contributions_unitemized":"37360.63",
  "col_b_total_individual_contributions":"110909.59",
  "col_b_political_party_contributions":"0.00",
  "col_b_pac_contributions":"1100.00",
  "col_b_candidate_contributions":"2750.00",
  "col_b_total_contributions":"114759.59",
  "col_b_transfers_from_authorized":"0.00",
  "col_b_candidate_loans":"0.00",
  "col_b_other_loans":"0.00",
  "col_b_total_loans":"0.00",
  "col_b_offset_to_operating_expenditures":"0.00",
  "col_b_other_receipts":"0.00",
  "col_b_total_receipts":"114759.59",
  "col_b_operating_expenditures":"88530.47",
  "col_b_transfers_to_authorized":"0.00",
  "col_b_candidate_loan_repayments":"0.00",
  "col_b_other_loan_repayments":"0.00",
  "col_b_total_loan_repayments":"0.00",
  "col_b_refunds_to_individuals":"1055.00",
  "col_b_refunds_to_party_committees":"0.00",
  "col_b_refunds_to_other_committees":"0.00",
  "col_b_total_refunds":"1055.00",
  "col_b_other_disbursements":"2010.00",
  "col_b_total_disbursements":"91595.47",
  "amendment":false,
  "form":"F3",
  "itemizations":{
    "SchA":[
      {
        "form_type":"SA11AI",
        "filer_committee_id_number":"C00654178",
        "transaction_id":"760417",
        "back_reference_tran_id_number":"",
        "back_reference_sched_name":"",
        "entity_type":"IND",
        "contributor_organization_name":"",
        "contributor_last_name":"Abedrabbo",
        "contributor_first_name":"Kamal",
        "contributor_middle_name":"",
        "contributor_prefix":"",
        "contributor_suffix":"",
        "contributor_street_1":"515 Verona Dr",
        "contributor_street_2":"",
        "contributor_city":"Rockford",
        "contributor_state":"IL",
        "contributor_zip":"611075307",
        "election_code":"P2018",
        "election_other_description":"",
        "contribution_date":"20171228",
        "contribution_amount":"1000.00",
        "contribution_aggregate":"1000.00",
        "contribution_purpose_descrip":"",
        "contributor_employer":"Twins Auto Mall",
        "contributor_occupation":"Principal",
        "donor_committee_fec_id":"",
        "donor_committee_name":"",
        "donor_candidate_fec_id":"",
        "donor_candidate_last_name":"",
        "donor_candidate_first_name":"",
        "donor_candidate_middle_name":"",
        "donor_candidate_prefix":"",
        "donor_candidate_suffix":"",
        "donor_candidate_office":"",
        "donor_candidate_state":"",
        "donor_candidate_district":"",
        "conduit_name":"",
        "conduit_street1":"",
        "conduit_street2":"",
        "conduit_city":"",
        "conduit_state":"",
        "conduit_zip":"",
        "memo_code":"",
        "memo_text_description":"",
        "reference_code":""
      }
    ],
    "SchB":[
      {
        "form_type":"SB17",
        "filer_committee_id_number":"C00654178",
        "transaction_id":"500018114",
        "back_reference_tran_id_number":"",
        "back_reference_sched_name":"",
        "entity_type":"ORG",
        "payee_organization_name":"ActBlue Technical Services",
        "payee_last_name":"",
        "payee_first_name":"",
        "payee_middle_name":"",
        "payee_prefix":"",
        "payee_suffix":"",
        "payee_street_1":"366 Summer St",
        "payee_street_2":"",
        "payee_city":"Somerville",
        "payee_state":"MA",
        "payee_zip":"021443132",
        "election_code":"P2018",
        "election_other_description":"",
        "expenditure_date":"20171107",
        "expenditure_amount":"29.67",
        "semi_annual_refunded_bundled_amt":"0.00",
        "expenditure_purpose_descrip":"Credit Card Processing FEe",
        "category_code":"",
        "beneficiary_committee_fec_id":"",
        "beneficiary_committee_name":"",
        "beneficiary_candidate_fec_id":"",
        "beneficiary_candidate_last_name":"",
        "beneficiary_candidate_first_name":"",
        "beneficiary_candidate_middle_name":"",
        "beneficiary_candidate_prefix":"",
        "beneficiary_candidate_suffix":"",
        "beneficiary_candidate_office":"",
        "beneficiary_candidate_state":"",
        "beneficiary_candidate_district":"",
        "conduit_name":"",
        "conduit_street_1":"",
        "conduit_street_2":"",
        "conduit_city":"",
        "conduit_state":"",
        "conduit_zip":"",
        "memo_code":"",
        "memo_text_description":"",
        "reference_to_si_or_sl_system_code_that_identifies_the_account":""
      }
    ]
  }
}
```
