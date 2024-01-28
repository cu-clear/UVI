This file contains instructions for setting up and maintaining the UVI and VN. If you find anything that is missed, please add them to this file.

About UVI (https://uvi.colorado.edu/):

1.	All codes for UVI website are stored at: https://github.com/cu-clear/UVI . Make sure you are a member of the group. 

2.	To set the website on your local machine:

(1)	Go to http: https://github.com/cu-clear/UVI.

(2)	Clone and cd into the deployable version of the UVI web app from the appropriate remote repository:

    git clone https://github.com/cu-clear/UVI
    cd UVI
(3)	Create a new conda environment for the UVI project, then activate the environment.
	
     conda create -n uvi_web python=3.6
     source activate uvi_web
(4)	With the conda environment active, update pip:

    pip install –upgrade pip
(5)	Install project dependencies from requirements.txt (unfortunately, conda doesn't have all the packages we need so instead of using two package managers we will use the active conda environment's copy of pip to manage our Python packages):

    pip install -r requirements.txt
(6)	Download Spacy English language model (necessary to generate dependency parse trees on VerbNet)
    python -m spacy download en

         python
         nltk.download('punkt')
(7)	Set environment variables for mail server:

    [MAIL_SETUP]
    mail_username = uvi.contact@gmail.com
    mail_password = VerbsAccount
    recipients = uvi.contact@gmail.com, martha.palmer@colorado.edu, brownsw@colorado.edu
(Or inject username and password from configs.ini file. NEVER, NEVER commit or upload this file anywhere.)
3.	Now the website has been set on your own local machine. You can run the server with commands below:

       cd ./UVI/uvi_web
       source activate uvi_web
       ./run_local.sh
   
   Copy and paste the localhost address to the browser. 
(This is also the way to test the website. Make sure it runs well before you push changes to https://github.com/cu-clear/UVI .)

4.	To deploy codes to the remote server: First please contact the Office of Information Technology (oithelp@colorado.edu)  to ask for the permission of verbs.colorado.edu server.

        ssh username@verbs.colorado.edu
        sudo su - verbnet-service
        cd UVI_deployable
        source activate uvi_web
        git remote -v (check whether the git upstream is https://github.com/cu-clear/UVI.git )
        git pull
        sudo service gunicorn_uvi reload
	
Now go to https://uvi.colorado.edu/, the changes should be reflected on the website.

More commands about remote server can be found at: https://docs.google.com/document/d/1p3nc_o7q4VfAD2RFu7OM8Xc9x8zvCPzIHoVur5ojkcM/edit?ts=5f861e3d
It also includes how to see if the database value has been uploaded.

5.	If you have any questions that are not mentioned in this documentation, please contact Lan Sang: lan.sang@colorado.edu


About VerbNet Website (https://verbs.colorado.edu/verbnet/):

1.	Here is the link for codes of VN Website: https://drive.google.com/file/d/1DiJbTxbIa5frby4a5SfbGF8R2N-hN6Wn/view?usp=sharing

2.	Commands to run and test the website on your local machine:

        cd verbnet_webpages_raw
        python -m http.server
	
	Copy and paste the localhost address to the browser and you can now test the website.
	
3.	To deploy codes to the remote server: First contact the Office of Information Technology (oithelp@colorado.edu)  to ask for the permission of verbs.colorado.edu server.

        ssh username@verbs.colorado.edu
        sudo su - verbnet-service
        cd /usr/local/apache/htdocs/verbs/verbnet/

(Because rewritting the folder requires additional permission, please contact Kevin Stowe to ask for it.)
