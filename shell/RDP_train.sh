cd /data/tdr/work/HMP
source activate py3
export CUDA_VISIBLE_DEVICES=0
nohup python train.py -i RDP/RTS16/input_data.txt -l RDP/RTS16/lables.txt -u RDP/RTS16/process_data_al.fa -a RDP/RTS16/annotation.txt -r RDP/RTS16/deepRank.txt -m 2 -k 10 -e 50 &
