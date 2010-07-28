echo off
cd ..
cd ..
cd ..
cd win
cd bin
del *.exe
del libsbml*.dll
del libsbml*.lib
del *.zip
del *.bz2
del *.gz
del *.xml
del *.ilk
del *.pdb
del *.exp
del csharp\*.*
del java\*.*
del perl\*.*
del python\python25\*.*
del python\python26\*.*
cd ..
cd ..
cd src
cd bindings

cd csharp
del libsbml_wrap-win.cpp
del charp-files-win\*.*
del *.zip
del *.bz2
del *.gz
del *.xml
cd ..

cd java
del java-files\*.*
del java-files\org\sbml\libsbml\*.*
del *.class
del libsbml_java_wrap.cpp
del *.zip
del *.bz2
del *.gz
del *.xml
del sbmlj.dll
del sbmlj.lib
cd ..

cd perl
del C:\Perl\lib\Libsbml.pm
del C:\Perl\lib\auto\libsbml\Libsbml.dll
del Libsbml.pm
del Libsbml.pod
del libsbml_perl_wrap.cpp
cd ..

cd python
del C:\Python\Python25\Lib\site-packages\_libsbml.*
del C:\Python\Python25\Lib\site-packages\libsbml.*
del C:\Python\Python26\Lib\site-packages\_libsbml.*
del C:\Python\Python26\Lib\site-packages\libsbml.*
del libsbml_python_wrap.cpp
del libsbml.py
del libsbml.pyc
del *.zip
del *.bz2
del *.gz
del *.xml
del test\annotation\*.pyc
del test\math\*.pyc
del test\sbml\*.pyc
del test\xml\*.pyc
cd ..

cd ..
cd ..
cd dev
cd utilities
cd nativeWinTests
