cd /data/tdr/work/HMP
source activate py3
nohup python RDPclassifier.py -i RDP/RTS16/process_data.fa -l RDP/RTS16/lables.txt -a RDP/RTS16/annotation.txt -r RDP/RTS16/deepRank.txt -c rdp_classifier_2.12/dist/classifier.jar -t RDP/RTS16/trainset16_db_taxid.txt -f RDP/RTS16/randomnum.txt -k 20 &
