date=$( date +%Y_%m_%d )
#echo ${date}
pic_name="plant-${date}.jpg"
fswebcam ${pic_name}
gsutil cp ${pic_name} gs://srmakerspace/
rm ${pic_name}
