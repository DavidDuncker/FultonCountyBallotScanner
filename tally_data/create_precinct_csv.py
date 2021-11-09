import csv


def csv_batch_rows_precinct_columns(precincts, csv_filepath):
    with open(csv_filepath, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        precinct_names = list(precincts["precinct data"].keys())
        #precinct_names.remove("all precincts")
        header = ["Tabulator", "Batch"]
        header.extend(precinct_names)
        csv_writer.writerow(header)
        tabulators = list(precincts.keys())
        tabulators.remove('precinct data')
        tabulators = list(map(int, tabulators))
        tabulators.sort()
        tabulators = list(map(str, tabulators))
        for tabulator in tabulators:
            if tabulator == "precinct data":
                continue
            batches = list(precincts[tabulator].keys())
            batches.remove('precinct data')
            try:
                batches.remove('')
            except ValueError:
                pass
            batches = list(map(int, batches))
            batches.sort()
            batches = list(map(str, batches))
            for batch in batches:
                if batch == "precinct data":
                    continue
                row = [tabulator, batch]
                for precinct_name in precinct_names:
                    row.append(precincts[tabulator][batch]["precinct data"][precinct_name]
                               ['President of the United States']["all candidates"])
                csv_writer.writerow(row)

    return True


def csv_precinct_rows_total_column(precincts, csv_file):
    pass
