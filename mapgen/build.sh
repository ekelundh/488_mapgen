java -jar ./lib/jflex-1.6.1.jar ./src/Scanner/maplang.flex

java -jar ./lib/java-cup-11b.jar -locations -xmlactions -interface -parser Parser -destdir ./src/Parser/ < ./src/Parser/maplang.cup

mkdir out

javac -d out -sourcepath src -cp "lib/java-cup-11b.jar:lib/jflex-1.6.1.jar" src/*.java

java -cp "out:lib/java-cup-11b.jar:lib/jflex-1.6.1.jar" Main examples/test1.pmap
java -cp "out:lib/java-cup-11b.jar:lib/jflex-1.6.1.jar" Main examples/test2.pmap
java -cp "out:lib/java-cup-11b.jar:lib/jflex-1.6.1.jar" Main examples/test3.pmap

