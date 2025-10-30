import glob
import re
import os
import getopt
import sys




def brat_load(filename):
    file_json_obj = {}
    file_json_obj['filename'] = filename

    max_chars = 0

    # compile for speed
    regex_text = re.compile('^([T|N])([0-9]+)')
    regex_source = re.compile('^Reference (T[0-9]+) Source:(.*):(.*)')
    regex_type = re.compile('^Reference (T[0-9]+) SemanticType:(.*):(.*)')
    regex_concept = re.compile('^Reference (T[0-9]+) ConceptId:(.*)')
    regex_temporality = re.compile('^Reference (T[0-9]+) Temporality:(.*)')
    regex_negated = re.compile('^Reference (T[0-9]+) Negated:(.*)')

    # build'JSON' object
    entities = {}
    file = open(filename, 'r', newline='\n')
    lines = file.readlines()
    for line in lines:

        tokens = line.strip().split('\t')
        textmatch = regex_text.findall(tokens[0])

        if len(textmatch) <= 0:
            print(f"WARNING: No data found in this line \"{line}\"")
            continue

        brattype, index = textmatch[0]

        if brattype == 'T':
            t_entity = tokens[0]
            entities[t_entity] = {}
            ner, start, end = tokens[1].split(' ')
            entities[t_entity]['location_start'] = int(start)
            entities[t_entity]['location_end'] = int(end)
            entities[t_entity]['text'] = tokens[2]
            entities[t_entity]['concept_id'] = {}
            entities[t_entity]['filename'] = filename
            max_chars = max(max_chars, int(end))

        if brattype == 'N':
            reference_match_source = regex_source.findall(tokens[1])
            if len(reference_match_source) > 0 and reference_match_source[0][0] == t_entity:
                concept_id = reference_match_source[0][1]
                source_id = reference_match_source[0][2]

                if concept_id not in entities[t_entity]['concept_id'].keys():
                    entities[t_entity]['concept_id'][concept_id] = {}
                if 'source' not in entities[t_entity]['concept_id'][concept_id].keys():
                    entities[t_entity]['concept_id'][concept_id]['source'] = []
                entities[t_entity]['concept_id'][concept_id]['source'].append(source_id)
                continue

            reference_match_type = regex_type.findall(tokens[1])
            if len(reference_match_type) > 0 and reference_match_type[0][0] == t_entity:
                concept_id = reference_match_type[0][1]
                semantic_type = reference_match_type[0][2]

                if concept_id not in entities[t_entity]['concept_id'].keys():
                    entities[t_entity]['concept_id'][concept_id] = {}
                if 'semantic_type' not in entities[t_entity]['concept_id'][concept_id].keys():
                    entities[t_entity]['concept_id'][concept_id]['semantic_type'] = []
                entities[t_entity]['concept_id'][concept_id]['semantic_type'].append(semantic_type)
                continue

            reference_match_concept = regex_concept.findall(tokens[1])
            if len(reference_match_concept) > 0 and reference_match_concept[0][0] == t_entity:
                concept_id = reference_match_concept[0][1]
                preferred_name = tokens[2]

                if concept_id not in entities[t_entity]['concept_id'].keys():
                    entities[t_entity]['concept_id'][concept_id] = {}
                if 'preferred_name' not in entities[t_entity]['concept_id'][concept_id].keys():
                    entities[t_entity]['concept_id'][concept_id]['preferred_name'] = preferred_name
                continue

            reference_match_temporality = regex_temporality.findall(tokens[1])
            if len(reference_match_temporality) > 0 and reference_match_temporality[0][0] == t_entity:
                temporality = reference_match_temporality[0][1]
                entities[t_entity]['temporality'] = temporality
                continue

            reference_match_negated = regex_negated.findall(tokens[1])
            if len(reference_match_negated) > 0 and reference_match_negated[0][0] == t_entity:
                negated_token = reference_match_negated[0][1]
                entities[t_entity]['negated'] = True
            else:
                entities[t_entity]['negated'] = False

    file_json_obj['max_chars'] = max_chars

    return entities


# take brat entities and make it concept focused vs text trigger focused

def collate(entities):
    concepts = {}

    for trigger in entities:

        negated = False
        recent = False
        historical = False
        if 'negated' in entities[trigger]:
            negated = True
        if entities[trigger]['temporality'] == 'Recent':
            recent = True
        if entities[trigger]['temporality'] == 'Historical':
            historical = True

        for concept in entities[trigger]['concept_id']:
            if concept in concepts:
                concepts[concept]['count'] = concepts[concept]['count'] + 1

            else:
                concepts[concept] = {}
                concepts[concept]['preferred_name'] = entities[trigger]['concept_id'][concept]['preferred_name']
                concepts[concept]['count'] = 1
                concepts[concept]['negated'] = 0
                concepts[concept]['recent'] = 0
                concepts[concept]['historical'] = 0

            if negated is True:
                concepts[concept]['negated'] = concepts[concept]['negated'] + 1
            if recent is True:
                concepts[concept]['recent'] = concepts[concept]['recent'] + 1
            if historical is True:
                concepts[concept]['historical'] = concepts[concept]['historical'] + 1

    return concepts



def outputCSV(input_file, output_file, header_array):
    
    # Check if output file exists
    file_exists = os.path.isfile(output_file)
    
    # Open file in appropriate mode (write or append)
    mode = "a" if file_exists else "w"
    output = open(output_file, mode)
    
    # Write header only if file doesn't exist
    if not file_exists:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arff_header = open(os.path.join(script_dir, 'big-blank.arff'), 'r')

        # copy the lines of arff_header to output
        for line in arff_header:
            output.write(line)  
        
        arff_header.close()
        print(f"Created new output file with ARFF header: {output_file}")
    else:
        print(f"Appending to existing file: {output_file}")
    
    id_number = 1
    

    print(f"Processing file: {input_file}")
    kept_cuis = {}  # Dictionary to store CUIs and their status
    docid = os.path.basename(input_file).replace(".ann", "")

    json_data = brat_load(input_file)
    c = collate(json_data)

    print(f"Processing {docid} with {len(c)} concepts")

    for cui in c:
        umls_preferred_name = c[cui]['preferred_name']
        occurences = c[cui]['count']
        negation_count = c[cui]['negated']
        recent_count = c[cui]['recent']
        historical_count = c[cui]['historical']

        if occurences == negation_count:
            status = "N"
        else:
            status = "P"

        weka_cui_name = "C_D_" + cui

        # print(f"CUI: {cui}, wekaCUI: {weka_cui_name}, Name: {umls_preferred_name}, Occurrences: {occurences}, Negated: {negation_count}, Recent: {recent_count}, Historical: {historical_count}, Status: {status}")
        if weka_cui_name in header_array:
            kept_cuis[weka_cui_name] = status

    kept_cui_row =  []
    for cui in header_array:
        if cui in kept_cuis:
            kept_cui_row.append(kept_cuis[cui])
            # print(f"Keeping {cui} with status {kept_cuis[cui]}")
        else:
            kept_cui_row.append("M")

    kept_cui_row[0] = str(id_number)
    id_number += 1
    
    ## output
    output.write(",".join(kept_cui_row) + "\n")
    output.close()

    print(f"Output complete: {output_file}")





def main():
    
    if len(sys.argv) < 2:

        print("Usage: ", sys.argv[0], "-i<input file> -o<output file>")
        print("     -i <filename> input .ann file")
        print("     -o <filename> output of arff file (appends if it exists)")
        sys.exit(0)

    input_file = None
    outputfile = None
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, 'i:o:')
    for name, value in opts:
        if name == '-i':
            input_file = value
        if name == '-o':
            outputfile = value

    if not input_file or not outputfile:
        print("Error: Both -i and -o arguments are required.")
        sys.exit(1)

    header_array = []
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, 'big-header.csv'), 'r') as f:
            # Parse header.csv into an array
            header_line = f.readline().strip()
            header_array = header_line.split(',')

    except FileNotFoundError:
        print("Warning: 'header.csv' not found.")
        exit(0)


    outputCSV(input_file, outputfile, header_array)

if __name__ == "__main__":
    main()