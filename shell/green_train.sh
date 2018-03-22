cd /data/tdr/work/HMP
source activate py3
export CUDA_VISIBLE_DEVICES=3
nohup python train.py -i GreenGene/97/input_data.txt -l GreenGene/97/lables.txt -u GreenGene/97/process_data.fa -a GreenGene/97/annotation.txt -r GreenGene/97/deepRank.txt -m 2 -k 10 -e 50 &
