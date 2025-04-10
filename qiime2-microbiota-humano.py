conda activate qiime2-amplicon-2024.10 #activar enviroment de qiime2

#################################  PASO 1: IMPORTAR DATOS ###########################3

#los archivos fastq deben tener un formato de CASAVA 1.8, que debe de ser: sampleid_barcode_L(lane-number)_R(read-number)_set-number.fastq.gz

#cd secuencias-humano/ #cambiar a la carpeta donde están las secuencias
gzip *.fastq #convertir todos los archivos fastq a gpzip para que lo pueda leer qiime

#nota: las secuencias con las que trabajie con pair-end, por los que es importante saber para los siguientes procesos
#nota 2: tenemos dos tipos de formatos, .qza (formato qiime, data artifact) y .qzv (formato para visualizar los artefactos de qiime)

qiime tools import   #importamos las secuencias
  --type 'SampleData[PairedEndSequencesWithQuality]' \   
  --input-path /home/gaby_torres/Documents/tesis-maestria/qiime2/secuencias-humano/ \   
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \  
  --output-path demux-paired-end.qza

qiime demux summarize \ #para poder visualizar las secuencias
  --i-data demux-paired-end.qza \
  --o-visualization demux-paired-end.qzv

qiime metadata tabulate \ #importar la metadata
    --m-input-file metadata-humano.tsv \
    --o-visualization metadata-humano.qzv

########################## PASO 2: DENOISING CON DADA2 ####################  

qiime dada2 denoise-paired \ # aplicar dada para quitar el ruido y recortar 
  --i-demultiplexed-seqs demux-paired-end.qza \
  --p-trunc-len-f 250 \ #caída de calidad de la sec forward 
  --p-trim-left-r 1 \ #en caso de que la secuencia tuviera todavía primer, para recortarlo  
  --p-trunc-len-r 240 \ #caída de calidad de la sec reverse 
  --o-representative-sequences asv-sequences-0.qza \
  --o-table feature-table-0.qza \
  --o-denoising-stats dada2-stats.qza
#este proceso tardo más de 5 horas en correr para 18 muestras, en una laptop de 16 gb de ram.

#este proceso genera 3 archivos, los cual vamos a generar su .qzv para poderlos visualizar

qiime metadata tabulate \
  --m-input-file dada2-stats.qza \
  --o-visualization dada2-stats-summ.qzv #resultados de filtrado
qiime feature-table summarize \
  --i-table feature-table-0.qza \
  --m-sample-metadata-file metadata-humano.tsv \
  --o-visualization feature-table-0-summ.qzv #asv's que funcionara para la asignacion
qiime feature-table tabulate-seqs \
  --i-data asv-sequences-0.qza \
  --o-visualization asv-sequences-0-summ.qzv #tabla de asv y abundancias

############### PASO 3: ASIGNACIÓN TAXONOMICA ###############################
# tenemos varias opciones de base de datos, como la SILVA o la Greengenes, en este caso vamos a usar a Greengenes 13-8
get \
  -O 'gg-13-8-99-515-806-nb-classifier.qza' \
  'https://docs.qiime2.org/jupyterbooks/cancer-microbiome-intervention-tutorial/data/030-tutorial-downstream/020-taxonomy/gg-13-8-99-515-806-nb-classifier.qza'
#descargamos la base de datos para la asignación taxonómica

qiime feature-classifier classify-sklearn \
  --i-classifier gg-13-8-99-515-806-nb-classifier.qza \ #nuestra base de datos
  --i-reads asv-sequences-0.qza \ #tabla de asv y abundancias 
  --o-classification taxonomy.qza #objeto ya con la asignación

#por default tiene un intervalo de confianza de 70%, el cual se puede cambiar, agregando el comando:
#   --p-confidence 

#para poder visualizar nuestro objeto que incluye la taxonomia:

qiime metadata tabulate \
  --m-input-file taxonomy.qza  \
  --o-visualization taxonomy.qzv

#ahora debemos filtrar los cloroplastos y mitocondrias

qiime taxa filter-table \
  --i-table feature-table-0.qza\
  --i-taxonomy taxonomy.qza \
  --p-mode contains \ 
  --p-include p__  \
  --p-exclude 'p__;,Chloroplast,Mitochondria' \
  --o-filtered-table feature-table-0-nomitochondria.pza #obteneos nuestra tabla de asv sin mitocondrias y cloroplastos


################## PASO 4: FILTRAR MUESTRAS CON BAJOS CONTEOS ########

qiime feature-table filter-samples \
  --i-table feature-table-0-nomitochondria.pza.qza \
  --p-min-frequency 500 \ #se filtran las secuencias con menos de 500 reads
  --o-filtered-table filtered-table-5.qza

################ PASO 5: GRAFICOS DE ABUNDANCIAS - BARPLOT #############################

qiime taxa barplot \ #grafico de abundancias relativas
  --i-table filtered-table-5.qza \
  --i-taxonomy taxonomy.qza \
  --m-metadata-file metadata-humano.tsv \
  --o-visualization taxa-bar-plots-2.qzv

qiime diversity alpha-rarefaction \ #grafica de rarefaccion
  --i-table filtered-table-5.qza  \
  --p-max-depth 2700 \ 
  --m-metadata-file metadata-humano.tsv \
  --o-visualization alpha-rarefaction.qzv

qiime feature-table rarefy \
  --i-table filtered-table-5.qza \
  --p-sampling-depth 800 \
  --o-rarefied-table asv-table-800.qza

qiime diversity alpha \
  --i-table asv-table-800.qza \
  --p-metric observed_features \
  --o-alpha-diversity observed-features-800.qza

qiime diversity alpha-group-significance \ # grafica de diversidad alfa 
  --i-alpha-diversity observed-features-800.qza \
  --m-metadata-file metadata-humano.tsv \
  --o-visualization observed-features-800.qzv

##### nuevo
qiime phylogeny align-to-tree-mafft-fasttree \
  --i-sequences asv-sequences-0.qza \
  --output-dir phylogeny-align-to-tree-mafft-fasttree

qiime diversity core-metrics-phylogenetic \
  --i-phylogeny phylogeny-align-to-tree-mafft-fasttree/rooted_tree.qza \
  --i-table filtered-table-5.qza \
  --p-sampling-depth 1103 \
  --m-metadata-file metadata-humano.tsv \
  --output-dir diversity-core-metrics-phylogenetic

qiime diversity alpha-group-significance \
  --i-alpha-diversity diversity-core-metrics-phylogenetic/faith_pd_vector.qza \
  --m-metadata-file metadata-humano.tsv \
  --o-visualization faith-pd-group-significance.qzv
qiime diversity alpha-group-significance \
  --i-alpha-diversity diversity-core-metrics-phylogenetic/evenness_vector.qza \
  --m-metadata-file metadata-humano.tsv \
  --o-visualization evenness-group-significance.qzv

qiime diversity beta-group-significance \
  --i-distance-matrix diversity-core-metrics-phylogenetic/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file metadata-humano.tsv \
  --m-metadata-column Tissue \
  --p-pairwise \
  --o-visualization unweighted-unifrac-tissue-group-significance.qzv

qiime taxa filter-table \
  --i-table feature-table-0.qza \
  --i-taxonomy taxonomy.qza \
  --p-include g__ \
  --o-filtered-table filtered-table-genus.qza

qiime metadata tabulate \
  --m-input-file filtered-table-genus.qza \
  --o-visualization filtered-genus.qzv

qiime feature-table filter-samples \
  --i-table filtered-table-genus.qza \
  --m-metadata-file metadata-humano.tsv \
  --p-where '[Tissue]="Human breast tumor"' \
  --o-filtered-table btumor-table.qza

