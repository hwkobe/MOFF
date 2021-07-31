#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modular prediction of off-target effects
@author: Wei He
@email: whe3@mdanderson.org
@Date: 05/31/2021
"""

__version__ = "1.0.0"
import os, argparse,textwrap,logging, sys,pkg_resources
from MOFF_prediction import *


def MOFFMain():
    ## Set logging format
    logging.basicConfig(level=logging.DEBUG,  
                    format='%(levelname)s:%(asctime)s @%(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='a')
    
    ## Add aruguments for user input with command lines.
    parser = argparse.ArgumentParser(description=
                                     "###############################################################################\n\n"
                                     
                                      "                  # # # # #   # # # #   # # # #  # # # # \n"
                                      "                  #   #   #   #     #   #        #       \n"
                                      "                  #   #   #   #     #   # # # #  # # # # \n"
                                      "                  #   #   #   #     #   #        #       \n"
                                      "                  #   #   #   # # # #   #        #       \n\n"
                                     
                                     "Hi,My name is MOFF, I'm good at prediction of off-target effects for \n" 
                                     "CRISPR/Cas9! Hope you enjoy playing with me ^o^!\n\n"
                                     
                                     "Any questions or bugs, please concat hwkobe.1027@gmail.com\n\n"
                                     
                                     "###############################################################################\n"
                                               
             ,formatter_class=argparse.RawTextHelpFormatter)
    
    ## Add subparser: moff score 
    subparsers =  parser.add_subparsers(help='commands to run MOFF',dest='subcmd')
    
    sub_score = subparsers.add_parser('score',help='Predict off-target effects for given gRNA-target pairs',
                                      formatter_class=argparse.RawTextHelpFormatter)
    
    #req_group = subp_call.add_argument_group(title='Required arguments for ProTiler call.',description='')
    sub_score.add_argument('-i','--inputfile',type=str,help="Input files containing sgRNA sequences and corresponding DNA target sequences.\n" "One gRNA(20bp+PAM) and one target(20bp+PAM) per line, .csv and .txt are accepted.\nMOFF is designed for mismatch-only off-target prediction, not for indel mutations. \nSee the following example:\n\n"
                                  
                                       "GAGTCCGAGCAGAAGAAGAATGG,GAGTCCAAGTAGAAGAAAAATGG\n"
                                       "GTTGCCCCACAGGGCAGTAAAGG,GTGGACACCCCGGGCAGGAAAGG\n"
                                       "GGGTGGGGGGAGTTTGCTCCAGG,AGGTGGGGTGAGTTTGCTCCAGG",required=True)
    
    sub_score.add_argument('-p','--prefix',type=str,help='Prefix of the file to save the outputs,default: ScoreTest',default='ScoreTest',required=False)
    sub_score.add_argument('-o','--outputdir',type=str,help="Directory to save output files,if no directory is given a folder named\nMOFF_scores will be generated in current working directory",default='MOFF_scores',required=False)
    
    sub_aggregation = subparsers.add_parser('aggregate',help='Predict the genome-wide off-target effects for given sgRNAs')
    
    sub_aggregation.add_argument('-i','--inputfile',type=str,help="MOFF aggregation can directly take the outputs of CRISPRitz as inputs. Besides, output table files generated by any genome-wide off-target searching methods such as Cas-OFFinder are supported in theory, but the columns of outputs for different methods are different, thus it is required to modify the column name of sgRNA(20bp+PAM) and target(20bp+PAM) to 'crRNA' and 'DNA' respectively. Note that MOFF only support mismatch-only off-target predictions, indel mutations are not applicable.File formats including .csv and .txt are accepted.",required=True)
    
    sub_aggregation.add_argument('-p','--prefix',type=str,help='Prefix of the file to save the outputs, default: AggregateTest',default='AggregateTest')
    sub_aggregation.add_argument('-o','--outputdir',type=str,help="Directory to save output files,if no directory is given, a output folder named\nMOFF_aggregation will be generated in current working directory",default='MOFF_aggragation')
    
    sub_allele = subparsers.add_parser('allele',help='Design sgRNAs for allele-specific knockouts',
                                      formatter_class=argparse.RawTextHelpFormatter)
    sub_allele.add_argument('-m','--mutant',type=str,help="Local DNA sequence of mutant allele, at least one hit of 20bp(mutation sites included)\nfollowed by PAM (NGG) should be included, if more than one hits found, MOFF will \ndesign sgRNAs based on all possible PAMs.",required=True)
    sub_allele.add_argument('-w','--wildtype',type=str,help="Local DNA sequence of wild type allele paired with the mutant allele,which should be \nthe same length of the mutant allele DNA sequence.",required=True)
    sub_allele.add_argument('-p','--prefix',type=str,help='Prefix of the file to save the outputs, default: AlleleTest.',default='AlleleTest')
    sub_allele.add_argument('-o','--outputdir',type=str,help="Directory to save output files,if no directory is given, a output folder named\nMOFF_aggregation will be generated in current working directory.",default='MOFF_Allele')
    
    args = parser.parse_args()
    
    if args.subcmd == None:
        parser.print_help()
        sys.exit(0)
        
    print("###############################################################################\n\n"
                                     
          "                  # # # # #   # # # #   # # # #  # # # # \n"
          "                  #   #   #   #     #   #        #       \n"
          "                  #   #   #   #     #   # # # #  # # # # \n"
          "                  #   #   #   #     #   #        #       \n"
          "                  #   #   #   # # # #   #        #       \n\n"
                                     
          "Hi,My name is MOFF, I'm good at prediction of off-target effects for \n" 
          "CRISPR/Cas9! Hope you enjoy playing with me ^o^!\n\n"
                                     
          "Any questions or bugs, please concat hwkobe.1027@gmail.com\n\n"
          
          "Now I got your command, let's go! \n\n"
                                     
          "###############################################################################\n")
    
    ## To generate the outputdir for saving result files
    try:
        os.mkdir(args.outputdir)
        logging.info('Creat the outputdir {} to place result files'.format(args.outputdir))
    except OSError:
        logging.warning('outputdir {} already exist'.format(args.outputdir))
    
    outputdir = os.path.join(os.getcwd(),args.outputdir) ## Set the path to outputdir
    prefix = args.prefix
    
    logging.info('Loading and reading mismatch-depdent matrix ...')
    m1_data = os.path.join(RequiredFilePath,'M1_matrix_dic_D9')
    m1_dic = json.loads(open(m1_data).read())
    
    logging.info('Loading and reading combinatorial effect matrix ...')
    m2_data = os.path.join(RequiredFilePath,'M2_matrix_smooth_MLE') 
    m2_dic = json.loads(open(m2_data).read())
    
    #logging.info('Loading pre-trained CNN model for GMT prediciton ...')
    #model = models.load_model(os.path.join(RequiredFilePath,'GOP_model_3.h5'))
        
    if args.subcmd == 'score':
        ## Obtain parameters from user input
        Inputfile =  args.inputfile
        if '.txt' in Inputfile:
            df_in = pd.read_csv(Inputfile, delimiter="\t", header=None, names=['crRNA', 'DNA'])
        elif '.csv' in Inputfile:
            df_in = pd.read_csv(Inputfile, header=None, names=['crRNA', 'DNA'])
        else:
            logging.error('Oops! Something wrong with the input file formats, accepted files includes .csv and .txt are accepted, would you please check and provide correct file format.')
            sys.exit(-1)
        
        logging.info("Reading the input gRNA-target pairs...")
        print(df_in)
        df_out = MOFF_score(m1_dic,m2_dic,df_in)
        df_out.to_csv(os.path.join(outputdir,prefix+'_MOFF.score.csv'))
        logging.info('^o^ Great! Job finished and results successfully saved, Check it in the output folder!')
       
        
    if args.subcmd == 'aggregate':
        ## Obtain parameters from user input
        Inputfile =  args.inputfile
                                 
        with open(Inputfile,'r') as f:
            firstline = f.readline()
            if 'crRNA' not in firstline or 'DNA' not in firstline:
                logging.error('!!! Input table should contain columns with name: crRNA \
                               and DNA to present sgRNA sequences and off-target sequences')
                sys.exit(-1)
        
        logging.info("Reading the input genome-wide off-targets table...")                         
        if '.txt' in Inputfile:
            df_in = pd.read_csv(Inputfile, delimiter="\t")
        elif '.csv' in Inputfile:
            df_in = pd.read_csv(Inputfile)
        else:
            logging.error('Oops! Something wrong with the input file formats, accepted files includes .csv and .txt are accepted, please provide correct file format.')
            sys.exit(-1)
        
        print(df_in)
        df_out = MOFF_aggregate(m1_dic,m2_dic,df_in)
        df_out.to_csv(os.path.join(outputdir,prefix+'_MOFF.aggregate.csv'))
        logging.info('^o^ Great! Job finished and results successfully saved, Check it in the output folder! Bye!')
        
if __name__ == '__main__':
    MOFFMain()    
