conda activate qiime2-amplicon-2024.10 #activar enviroment de qiime2

####      Importar datos

#cd secuencias-humano/ #cambiar a la carpeta donde están las secuencias
gzip *.fastq #transformar las secuencias para poderlas leer

qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path /home/gaby_torres/Documents/tesis-maestria/qiime2/secuencias-humano/ \
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \ 
  --output-path demux-paired-end.qza

#Para poder visualizar las secuencias

qiime demux summarize \
  --i-data demux-paired-end.qza \
  --o-visualization demux-paired-end.qzv

#subir la tabla de metadatos
qiime metadata tabulate \ 
    --m-input-file metadata.tsv \
    --o-visualization metadata.qzv


####      Control de calidad


qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux-paired-end.qza \
  --p-trunc-len-f 250 \
  --p-trim-left-r 1 \
  --p-trunc-len-r 240 \
  --o-representative-sequences rep-seqs.qza \
  --o-table table.qza \
  --o-denoising-stats denosing-stats.qza

#este proceso genera 3 archivos, los cual vamos a generar su .qzv para poderlos visualizar

#resultados de filtrado
qiime metadata tabulate \
  --m-input-file denosing-stats.qza \
  --o-visualization denosing-stats.qzv 

#asv's que funcionara para la asignacion
qiime feature-table summarize \
  --i-table table.qza \
  --m-sample-metadata-file metadata.tsv \
  --o-visualization table.qzv

#tabla de asv y abundancias
qiime feature-table tabulate-seqs \
  --i-data rep-seqs.qza \
  --o-visualization rep-seqs.qzv

####      Asignación taxonómica

wget \
  -O 'gg-13-8-99-515-806-nb-classifier.qza' \
  'https://docs.qiime2.org/jupyterbooks/cancer-microbiome-intervention-tutorial/data/030-tutorial-downstream/020-taxonomy/gg-13-8-99-515-806-nb-classifier.qza'
#descargamos la base de datos para la asignación taxonómica

qiime feature-classifier classify-sklearn \
  --i-classifier gg-13-8-99-515-806-nb-classifier.qza \
  --i-reads rep-seqs.qza \
  --o-classification taxonomy.qza

qiime metadata tabulate \
  --m-input-file taxonomy.qza \
  --o-visualization taxonomy.qzv


