#! /usr/bin/python 
#####Plz run this script in python 3
##################
#####Inverse Translation for the protein FASTA files
#####Yifan Ethan Chen
#####BioE 131 HW2
#####09/24/17 Cal

import sys,re, time, math, copy, os, re
from sys import exit
from sys import argv

#####for codon sorting
def frequence(s): 
    return s[2]

#####chosing the best codon by frequency and repeat penalty
def chooseaa_non1st(aa):
    score_list_aa = []
    for info in codondict[aa]:
        score_codon = info[1] - 1/(aan - seqcodondict[info[0]][-1])
        score_list_aa.append(score_codon)
    best_score = max(score_list_aa)
    codon = codondict[aa][score_list_aa.index(best_score)][0]
    return codon, best_score


#####Error Handle
try: 
    proteinfile_name = sys.argv[1]
except IndexError:
    print ('The user did not specify a FASTA file argument on the command line.')
    sys.exit()
try: 
    codontablefile_name = sys.argv[2]
except IndexError:
    print ('The user did not specify a codon usage table file argument on the command line.')
    sys.exit()
try:
    fin = open(proteinfile_name)
    fin = open(codontablefile_name)
except IOError:
    print ('The file named by the user does not exist, or is not readable.')
    sys.exit()

    
proteinfile = open(proteinfile_name) 
proteincontents = proteinfile.readlines()
codontablefile = open(codontablefile_name)
codontablecontents = codontablefile.readlines()
pattern = re.compile(r'\(-(.+?)\)')


#####build codon dict
print ('Reading codon usage table..')
codondict = {}
codonforseq = {}   #the first element is math.log10(freq)
for line in codontablecontents:
    line = line.rstrip()
    line = re.split('[()]',line)
    if line[-1] =='':
        line.pop()
    if line:
        codonlist = [line[i] for i in range(0,len(line),2)]
        for i in codonlist:
            i = i.split()
            if i[1] in codondict.keys():
                if float(i[2]) != 0:
                    codondict[i[1]].append((i[0], math.log10(float(i[2])), float(i[3])))   #codon, probability, frequence
                    codonforseq.setdefault(i[0], [math.log10(float(i[2]))])
            else:
                if float(i[2]) != 0:
                    codondict.setdefault(i[1], [(i[0], math.log10(float(i[2])), float(i[3]))])
                    codonforseq.setdefault(i[0], [math.log10(float(i[2]))])
for i in codondict.keys():
    k = sorted(codondict[i], key = frequence, reverse = True)
    codondict[i] = k


#####protein sequence read
print ('Reading protein sequence(s)..')
proteinlist = []
n = 0
while n < len(proteincontents):
    if proteincontents[n] == '\n':
        n += 1
    elif proteincontents[n][0] == '>':
        proteinname = proteincontents[n].split()[0]
        sequence = ''
        n += 1
        while n < len(proteincontents) and proteincontents[n][0] !='>':
            sequence += proteincontents[n].rstrip()
            n += 1
        if n < len(proteincontents) and proteincontents[n][0] == '>' and sequence == '':
            print ('No sequence for ' + proteinname[1:] + '.')
        else:
            for aa in sequence:
                if aa.upper() in ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']:
                    pass
                else:
                    print ('The file named by the user contains sequence ' + proteinname[1:] + ' that is not protein.')
                    sys.exit()
            proteinlist.append((proteinname,sequence.upper()))
    elif contents[n][0] != '>':
        print ('The file named by the user is not in FASTA format.')
        sys.exit()


#####find the best codons to generate sequence
print ('Doing inverse translation for input sequence(s)...')
report = []
for protein in proteinlist:
    score, aan = 0, 0
    seqcodondict = copy.deepcopy(codonforseq)   #the first element is math.log10(freq)
    proteinname, proteinseq = protein
    RNAseq = ''
    start = time.time()
    for aa in proteinseq:
        if len(seqcodondict[codondict[aa][0][0]]) == 1:
            codon, score_1 = codondict[aa][0][0], codondict[aa][0][1]
        else:
            codon, score_1 = chooseaa_non1st(aa)
        RNAseq += codon
        score += score_1
        seqcodondict[codon].append(aan)
        aan += 1
    
    RNAseq += codondict['*'][0][0]
    elapsed = (time.time() - start)
    #####calculate RNA structure
    tempfile = open('temp.fa', 'w')
    tempfile.write(RNAseq)
    tempfile.close()
    os.system('rm -rf temp.fold rna.ps')
    os.system('RNAfold -i temp.fa -o temp -T 20')
    structurescore_file = open('temp.fold').read()
    structurescore = float(pattern.findall(structurescore_file)[0])
    os.system('rm -rf temp.fold rna.ps temp.fold temp.fa')
    #####calculate final score
    score = score - structurescore - 10*elapsed
    report.append((proteinname, RNAseq, score))


#####write output
print ('Writing output file ' + proteinfile_name + '_output.fa ...')
fout = open(proteinfile_name+'_output.fa', 'w')
for i_report in report:
    proteinname, RNAseq, score = i_report
    fout.write(proteinname+'\n')
    seqlist = [RNAseq[i:i+80]+'\n' for i in range(0,len(RNAseq),80)]
    for i_seqlist in seqlist:
        fout.write(i_seqlist)
fout.close()
sys.exit()
