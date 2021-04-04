
import requests
from bs4 import BeautifulSoup
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio import SeqIO
import numpy as np


def extract_sequnece_from_genus(name1, name2):

    name1 = name1.lower()
    name2 = name2.lower()

    full_sequence_file = f"{name2}_full_sequence_file.fas"
    fw = open(full_sequence_file, "w", encoding="utf8")
    sixteen_sequence_file = f"{name2}_sequence_file_1.fas"
    f = open(sixteen_sequence_file, "w", encoding="utf8")

    LPSN_result = requests.get(f"https://lpsn.dsmz.de/genus/{name2}")

    LPSN_soup = BeautifulSoup(LPSN_result.text, "lxml")

    NAME_genus_list = []
    NAME_2_genus_list = []

    genus_NAME = LPSN_soup.find_all("a", {"class": "color-species"})
    genus_NAME_2 = LPSN_soup.find_all("td")

    len_list = []
    lpsn_genus_list = []
    lpsn_final_list = []

    for n in genus_NAME:
        NAME_genus_list.append(n.get_text())

    for j in genus_NAME_2:
        NAME_2_genus_list.append(j.get_text())

    n = 3
    result_not = [NAME_2_genus_list[i * n:(i + 1) * n]
                  for i in range((len(NAME_2_genus_list) + n - 1) // n)]
    result_fin = []
    for i in result_not:
        if "synonym" in i:
            continue
        elif "misspelling" in i:
            continue
        elif "basonym" in i:
            continue
        elif "validly published" and "correct name" in i:
            result_fin.append(i)
        elif "not validly published" in i:
            result_fin.append(i)

    valid_name_list = sum(result_fin, [])

    lpsn_genus_list.append(
        set([i for i in NAME_genus_list for j in valid_name_list if i == j]))

    for i in lpsn_genus_list:
        c_list = list(i)

    genus_list = []
    sp_list = []
    strain_list = []
    accession_list = []
    for j in c_list:
        d_list = "".join(j)
        lpsn_final_list.append(d_list)
        lpsn_final_species_list = d_list.split(" ")
        lpsn_final_species_list[0] = lpsn_final_species_list[0].replace(
            '"', "")
        lpsn_final_species_list[1] = lpsn_final_species_list[1].replace(
            '"', "")
        genus_list.append(lpsn_final_species_list[0])
        sp_list.append(lpsn_final_species_list[1])

        try:

            url = f"https://lpsn.dsmz.de/species/{lpsn_final_species_list[0].lower()}-{lpsn_final_species_list[1].lower()}"
            modi_url = url.replace('"', "").replace("[", "").replace("]", "")
            LPSN_species_result = requests.get(modi_url)

            LPSN_species_soup = BeautifulSoup(
                LPSN_species_result.text, "html.parser")
            gene_site_list = LPSN_species_soup.find_all(
                "a", {"class": "url-sequence"})  # not exist : index error

            if gene_site_list == []:
                print(
                    f"{lpsn_final_species_list[0]}, {lpsn_final_species_list[1]}'s EBI URL can't find")
                genus_list.pop()
                sp_list.pop()
                continue

            else:
                ebi_site_list = []
                ebi_site = []

                for i in gene_site_list:
                    ebi_site_list.append(i.get("href"))

                for i in ebi_site_list:
                    if "ebi" in i:
                        ebi_site.append(i)

                modi_site = str(ebi_site[0])

                ebi_result = requests.get(modi_site)

                #ebi_soup = BeautifulSoup(ebi_result.text, "lxml")

                modi_fasta_site = modi_site.replace("view/", "api/fasta/")
                Accession_Number_1 = modi_fasta_site.replace(
                    "https://www.ebi.ac.uk/ena/browser/api/fasta/", "")
                accession_list.append(Accession_Number_1.replace(
                    Accession_Number_1, f"({Accession_Number_1})"))
                modi_EMBL_site = modi_site.replace("view/", "api/embl/")
                ebi_EMBL_result = requests.get(modi_EMBL_site)
                ebi_EMBL_soup = []
                ebi_EMBL_soup = BeautifulSoup(ebi_EMBL_result.text, "lxml")

                aa = []
                Strain_Name = []

                if ebi_EMBL_soup == []:
                    print(
                        f"{lpsn_final_species_list[0]}, {lpsn_final_species_list[1]}'s EMBL site can't find")
                    genus_list.pop()
                    sp_list.pop()
                    accession_list.pop()
                    continue

                else:
                    for i in ebi_EMBL_soup:
                        aa.append(i.get_text().strip())

                    bb = "".join(aa)
                    bb = bb.replace("/", "").replace("\n",
                                                     "").replace("FT", "")

                    cc = bb.split("    ")

                    for i in cc:

                        if "strain=" in i:
                            Strain_Name.append(i.replace('"', "").replace("strain=", "").replace("type strain: ", "").replace(
                                "type strain:", "").replace(" type strain:", "").replace("   ", "").replace("    ", "").replace("rRNA", ""))

                        elif "tissue_lib=" in i:
                            Strain_Name.append(i.replace('"', "").replace("tissue_lib=", "").replace("type strain: ", "").replace(
                                "type strain:", "").replace(" type strain:", "").replace("   ", "").replace("    ", "").replace("rRNA", ""))

                        elif "isolate=" in i:
                            Strain_Name.append(i.replace('"', "").replace("isolate=", "").replace("type strain: ", "").replace(
                                "type strain:", "").replace(" type strain:", "").replace("   ", "").replace("    ", "").replace("rRNA", ""))

                        elif "clone=" in i:
                            Strain_Name.append(i.replace('"', "").replace("clone=", "").replace("type strain: ", "").replace(
                                "type strain:", "").replace(" type strain:", "").replace("   ", "").replace("    ", "").replace("rRNA", ""))

                    if "=" in Strain_Name[0]:
                        strain_split = Strain_Name[0].split(" = ")
                        strain_list.append(strain_split[0])

                    elif ";" in Strain_Name[0]:
                        strain_split = Strain_Name[0].split(";")
                        strain_list.append(strain_split[0])

                    else:

                        strain_list.append(str(Strain_Name[0]))

                    ebi_site_result = requests.get(modi_fasta_site)
                    ebi_site_soup = []
                    ebi_site_soup = BeautifulSoup(ebi_site_result.text, "lxml")

                    if ebi_site_soup == []:
                        print(
                            f"{lpsn_final_species_list[0]}, {lpsn_final_species_list[1]}' FASTA  site can't find")
                        genus_list.pop()
                        sp_list.pop()
                        strain_list.pop()
                        accession_list.pop()
                        continue

                    else:

                        sixteen_S_rRNA = ebi_site_soup.get_text().strip()

                        if len(sixteen_S_rRNA) > 3000:

                            genus_list.pop()
                            sp_list.pop()
                            strain_list.pop()
                            accession_list.pop()

                            # fw.write(f"""{sixteen_S_rRNA}""")
                            print(
                                f"{lpsn_final_species_list[0]}, {lpsn_final_species_list[1]}'s sequence too long")

                        else:
                            len_list.append(sixteen_S_rRNA)
                            f.write(f"""{sixteen_S_rRNA}

""")

        except IndexError:
            print(
                f"{lpsn_final_species_list[0]}, {lpsn_final_species_list[1]}'s species can't find")
            genus_list.pop()
            sp_list.pop()
            accession_list.pop()
            # strain_list.pop()

    f.close()
    fw.close()

    #print(f"Total 16S_rRNA_Sequence of {name2} : ",len(len_list))

    #print("genus:", len(genus_list))
    #print("sp:", len(sp_list))
    #print("strain:", len(strain_list))
    #print("accession:", len(accession_list))

    return sixteen_sequence_file, genus_list, sp_list, strain_list, accession_list


'''
def modification_fasta_format(file_name) :
    modi_file = extract_sequnece_from_genus("genus","Abditibacterium")
    with open(modi_file) as fh:
        for record in SeqIO.parse(fh, 'fasta'):
            seq = record.seq
            for i in seq_:
                record = SeqRecord(Seq(seq_),sp_name, description = strain_name +" "+ Accession_Number)
                SeqIO.write(record,fh_out, "fasta" )
    
return modi_file'''


def Mod_Sequence_file(name1, name2):

    sequence_info, genus_info, sp_info, strain_info, accession_info = extract_sequnece_from_genus(
        name1, name2)
    file_name = "16S_rRNA_seq.txt"
    fw = open(file_name, "w", encoding="utf8")
    sequence = []
    Name_info = []
    final_info = []
    record = np.arange(len(sp_info), dtype=int)

    #print("genus:", len(genus_info))
    #print("sp:", len(sp_info))
    #print("strain:", len(strain_info))
    #print("accession:", len(accession_info))

    with open(sequence_info) as fh:

        for i in SeqIO.parse(fh, "fasta"):

            sequence.append(str(i.seq))

        #SeqIO.write(record, f_out,'fasta')

    print("seq: ",  len(sequence))

    for i in record:
        Name = genus_info[i] + " " + sp_info[i]
        description = strain_info[i] + " " + accession_info[i]
        Name_description = Name + " " + description
        Name_info.append(Name_description)

    for i in record:
        final_info.append(
            ">"+str(Name_info[i].replace('"', "")) + "\n" + str(sequence[i])+"\n\n")

    for i in final_info:

        fw.write(str(i))

    fw.close()
    blank_list = []
    for i in range(0, len(Name_info)):

        data_dict = {}
        data_dict["name"] = Name_info[i]
        data_dict["sequence"] = sequence[i]
        blank_list.append(data_dict)

    return blank_list
