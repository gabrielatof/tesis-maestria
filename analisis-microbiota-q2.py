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

####     Análisis de diversidad
#Instalar el env kmerizer para realizar los análisis 
sudo apt install git

git clone https://github.com/bokulich-lab/q2-kmerizer.git
cd q2-kmerizer

conda env create --name q2-kmerizer-amplicon-2024.10 --file https://raw.githubusercontent.com/bokulich-lab/q2-kmerizer/refs/heads/main/environment-files/q2-kmerizer-qiime2-amplicon-2024.10.yml

conda activate q2-kmerizer-amplicon-2024.10

make install

qiime kmerizer core-metrics \
    --i-sequences sequences-no-mitochondria-no-chloroplast.qza \
    --i-table table-no-mitochondria-no-chloroplast.qza \
    --p-sampling-depth 2000 \
    --m-metadata-file metadata.tsv \
    --p-color-by Tissue \
    --p-max-features 5000 \
    --output-dir core-metrics/ #en esta carperta se encuentran todos los artefactos de los análisis

conda deactivate

conda activate qiime2-amplicon-2024.10

#Visualización de diversidad alfa

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics/shannon_vector.qza \
  --m-metadata-file metadata.tsv \                                              
  --o-visualization core-metrics/shannon_vector.qzv


qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics/observed_features_vector.qza \
  --m-metadata-file metadata-humano.tsv \
  --o-visualization core-metrics/observed_features_vector.qzv

#Visualización de diversidad beta
qiime diversity beta-group-significance \
  --i-distance-matrix core-metrics/jaccard_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --m-metadata-column Tissue \
  --p-pairwise \
  --o-visualization core-metrics/jaccard_distance_matrix.qzv

qiime emperor plot \
  --i-pcoa core-metrics/bray_curtis_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/bray_curtis_pcoa_results.qzv


qiime diversity beta-group-significance \
  --i-distance-matrix core-metrics/bray_curtis_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --m-metadata-column Tissue \
  --p-pairwise \
  --o-visualization core-metrics/bray_curtis_distance_matrix.qzv

qiime emperor plot \
  --i-pcoa core-metrics/bray_curtis_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/bray_curtis_pcoa_results.qzv

qiime diversity adonis \
  --i-distance-matrix core-metrics/jaccard_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/jaccard_adonis.qzv \
  --p-formula Tissue


####      Análisis taxonómicos

qiime taxa barplot \
  --i-table table.qza \
  --i-taxonomy taxonomy.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-plots.qzv



##############################################################################################################################################
########################### REPETICIÓN DE ANÁLISIS A NIVEL DE GENÉRO #########################################################################
##############################################################################################################################################


#Filtrar la tabla de ASV para tener unicamente a nivel genero
qiime taxa filter-table \
  --i-table table-no-mitochondria-no-chloroplast.qza \
  --i-taxonomy taxonomy.qza \
  --p-include g__ \
  --o-filtered-table analisis-genus/filtered-table-genus.qza

#para visualizarlo
qiime feature-table summarize \
  --i-table analisis-genus/filtered-table-genus.qza \
  --m-sample-metadata-file metadata.tsv \
  --o-visualization analisis-genus/filtered-table-genus.qzv

#Filtrar secuencias de ASV para tener unicamente las de nivel genero
qiime taxa filter-seqs \
  --i-sequences sequences-no-mitochondria-no-chloroplast.qza \
  --i-taxonomy taxonomy.qza \
  --p-include g__ \
  --o-filtered-sequences analisis-genus/filtered-seqs-genus.qza

#Para visualizarlo
qiime feature-table tabulate-seqs \
  --i-data analisis-genus/filtered-seqs-genus.qza \
  --o-visualization analisis-genus/filtered-seqs-genus.qzv

#Analisis de diversidad 
conda activate q2-kmerizer-amplicon-2024.10

qiime kmerizer core-metrics \
    --i-sequences filtered-seqs-genus.qza \
    --i-table filtered-table-genus.qza \
    --p-sampling-depth 170 \
    --m-metadata-file metadata.tsv \
    --p-color-by Tissue \
    --p-max-features 5000 \
    --output-dir core-metrics/ 

conda deactivate

conda activate qiime2-amplicon-2024.10

cd analisis-genus/

#Visualización de diversidad alfa

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics/shannon_vector.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/shannon_vector.qzv

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics/observed_features_vector.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/observed_features_vector.qzv

#Visualización de diversidad beta
qiime diversity beta-group-significance \
  --i-distance-matrix core-metrics/jaccard_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --m-metadata-column Tissue \
  --p-pairwise \
  --o-visualization core-metrics/jaccard_distance_matrix.qzv

qiime emperor plot \
  --i-pcoa core-metrics/bray_curtis_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/bray_curtis_pcoa_results.qzv


qiime diversity beta-group-significance \
  --i-distance-matrix core-metrics/bray_curtis_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --m-metadata-column Tissue \
  --p-pairwise \
  --o-visualization core-metrics/bray_curtis_distance_matrix.qzv

qiime emperor plot \
  --i-pcoa core-metrics/bray_curtis_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics/bray_curtis_pcoa_results.qzv

#### Analisis taxónomicos
  
qiime taxa barplot \
  --i-table filtered-table-genus.qza \
  --i-taxonomy taxonomy.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-plot-genus.qzv

  #### Alpha rarefaction
  qiime diversity alpha-rarefaction \
  --i-table filtered-table-genus.qza\
  --p-max-depth 600 \
  --m-metadata-file metadata.tsv \
  --o-visualization alpha-rarefaction.qzv

  #### Abundancias diferenciales
qiime composition ancombc \
  --i-table filtered-table-genus.qza \
  --m-metadata-file metadata.tsv \
  --p-formula Tissue \
  --o-differentials ancombc.qza
qiime composition da-barplot \
  --i-data ancombc.qza \
  --o-visualization da-barplot.qzv

#anotación de lqa taxonomia a nivel genero
 qiime taxa collapse \
  --i-table filtered-table-genus.qza \
  --i-taxonomy ~/Documents/tesis-maestria/qiime2-segundo-ejercicio/taxonomy.qza \
  --p-level 6 \
  --o-collapsed-table table-level6.qza

  qiime composition ancombc \
  --i-table table-level6.qza \
  --m-metadata-file metadata.tsv \
  --p-formula Tissue \
  --o-differentials ancombc-level6.qza

  qiime composition da-barplot \
  --i-data ancombc-6l.qza \
  --o-visualization level6-da-barplot.qzv

#a nivel especie
qiime taxa collapse \
  --i-table filtered-table-genus.qza \
  --i-taxonomy ~/Documents/tesis-maestria/qiime2-segundo-ejercicio/taxonomy.qza \
  --p-level 7 \
  --o-collapsed-table table-level7.qza

  qiime composition ancombc \
  --i-table table-level7.qza \
  --m-metadata-file metadata.tsv \
  --p-formula Tissue \
  --o-differentials ancombc-level7.qza

  qiime composition da-barplot \
  --i-data ancombc-7l.qza \
  --o-visualization level7-da-barplot.qzv

  ####      Abundancias relativas
  qiime feature-table relative-frequency \
  --i-table table-level6.qza \
  --o-realtive-frequency-table rel-table.qza 
  #Esa tabla contiene las abundancias en relativa frecuencia

qiime tools export --input-path rel-table.qza --output-path exported
# Para conseguir la tabla en un archivo tsv primero exportamos los datos en formato biom

biom convert -i exported/feature-table.biom -o exported/feature-table.tsv --to-tsv #tenemos la tabla de abundancias relativas en una tabla en formato tsv 
  

  
