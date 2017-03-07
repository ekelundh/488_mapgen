java -jar ./lib/jflex-1.6.1.jar ./src/Scanner/maplang.flex

java -jar ./lib/java-cup-11b.jar -locations -xmlactions -interface -parser Parser -destdir ./src/Parser/ < ./src/Parser/maplang.cup

mkdir out

javac -d out -sourcepath src -cp lib/java-cup-11b.jar;lib/jflex-1.6.1.jar src/*.java

java -cp out;lib/java-cup-11b.jar;lib/jflex-1.6.1.jar Main examples/test1.pmap
java -cp out;lib/java-cup-11b.jar;lib/jflex-1.6.1.jar Main examples/test2.pmap
java -cp out;lib/java-cup-11b.jar;lib/jflex-1.6.1.jar Main examples/test3.pmap

cd python_codegen

mkdir out

python pmapCodeGenerator.py ../examples/test1.xml ./out/test1.lay test1
python test1.py

python pmapCodeGenerator.py ../examples/test3.xml ./out/test3.lay test3
python test3.py

python pmapCodeGenerator.py ../examples/test2.xml ./out/test2.lay test2
python test2.py

cd ..
