#! /bin/bash


for i in `seq 1923 2016`;
do
	wget -c https://www.data.jma.go.jp/svd/eqev/data/bulletin/data/shindo/i${i}.zip
done
