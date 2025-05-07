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

#El siguiente paso es eliminar las mitocondrias y los cloroplastos de las secuencias y las tablas de ASV
qiime taxa filter-table \
  --i-table table.qza \
  --i-taxonomy taxonomy.qza \
  --p-exclude mitochondria,chloroplast \
  --o-filtered-table table-no-mitochondria-no-chloroplast.qza

qiime taxa filter-seqs \
  --i-sequences rep-seqs.qza \
  --i-taxonomy taxonomy.qza \
  --p-exclude mitochondria,chloroplast \
  --o-filtered-sequences sequences-no-mitochondria-no-chloroplast.qza

####      Generación árbol filognético

wget \
  -O "sepp-refs-gg-13-8.qza" \
  "https://data.qiime2.org/classifiers/sepp-ref-dbs/sepp-refs-gg-13-8.qza" 
#descargamos una base de referencia para la generación del árbol

qiime fragment-insertion sepp \
  --i-representative-sequences equences-no-mitochondria-no-chloroplast.qza \
  --i-reference-database sepp-refs-gg-13-8.qza \
  --o-tree tree.qza \
  --o-placements tree_placements.qza \
  --p-threads 1  
