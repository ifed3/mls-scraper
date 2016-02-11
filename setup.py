from distutils.core import setup
import py2exe

setup(console=[
                {
                    "script":   'gui.py',
                    "dest_base":    "Shadow Market Scraper"
                }
            ],
        options={
            "py2exe":{
                "packages": ["lxml", "sip"] #Pacakges that need to be included
            }
        }
    )
