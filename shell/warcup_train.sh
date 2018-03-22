cd /data/tdr/work/HMP
source activate py3
export CUDA_VISIBLE_DEVICES=3
nohup python train.py -i RDP/Warcup2/input_data.txt -l RDP/Warcup2/lables.txt -u RDP/Warcup2/process_data_al.fa -a RDP/Warcup2/annotation.txt -r RDP/Warcup2/deepRank.txt -m 2 -k 10 -e 50 &
