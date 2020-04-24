from setuptools import setup, find_packages 
import re

with open('requirements.txt') as f: 
	requirements = f.readlines() 

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")
    
setup( 
		name ='autolive', 
		version ='0.0.3', 
		author ='Pablo Voorvaart', 
		author_email ='pablo.voorvaart@gmail.com', 
		url ='https://github.com/pabloVoorvaart/Autolive.git', 
		description ='Dev Package for autolive', 
		long_description = long_descr, 
		license ='MIT', 
		entry_points ={ 
			'console_scripts': [ 
				'autolive = Autolive.autolive:main'
			] 
		}, 
		classifiers =( 
			"Programming Language :: Python :: 3", 
			"License :: OSI Approved :: MIT License", 
			"Operating System :: OS Independent", 
		),
      	packages=find_packages(),
		python_requires='>=3.6',  
		install_requires = requirements, 
		zip_safe = False
) 
