cd /data/tdr/work/HMP
source activate py3
nohup python RDPclassifier.py -i RDP/Warcup2/process_data.fa -l RDP/Warcup2/lables.txt -a RDP/Warcup2/annotation.txt -r RDP/Warcup2/deepRank.txt -c rdp_classifier_2.12/dist/classifier.jar -t RDP/Warcup2/Warcup_v2_RDP_Taxonomy.txt -f RDP/Warcup2/randomnum.txt -k 10 &
