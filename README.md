* Revisar que la versión de Python sea 3.10 o mayor:
```
python --version
```

* Instalar el paquete pip de Python3:
```
sudo apt install python3-pip
```

* Instalar entorno virtual:
```
pip3 install virtualenv
```

* Crear carpeta de test
```
mkdir test && cd test
```

* Crear entorno vitual:
```
virtualenv .entornoVirtual
```

* Clonar el repositorio:
``` 
git clone https://github.com/malcovarela00/test.git
```

* Instalar dependencias en el entorno virtual:
```
pip install -r requirements.txt
```

* Ecutar script:
```
python main.py https://www.larodan.com/products/category/monounsaturated-fa/
```
o
```
python main2.py https://www.larodan.com/products/category/monounsaturated-fa/
```