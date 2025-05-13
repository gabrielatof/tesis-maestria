############################ 
#Instalación de q2-micom
##############################

#Asumimos que se tiene instalado previamente qiime 2 versión de amplicon, en este caso qiime2-amplicon-2024.10

wget https://raw.githubusercontent.com/micom-dev/q2-micom/main/q2-micom-linux.yml

conda env update -n qiime2-amplicon-2024.10 -f q2-micom-linux.yml

rm q2-micom-*.yml #eliminar el archivo 

conda activate qiime2-amplicon-2024.10 

##################
