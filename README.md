# Multi-user Blog

This project can be used to set up a multiple user blog. You can view a live version of this application [here](https://blog-project-151202.appspot.com/blog)

## Software used

-Python 2.7, specifically, [Anaconda](https://www.continuum.io/downloads) -Google App Engine SDK -Jinja2 templating language

## Quick start

You will first need to create an account for the [Google Cloud Platform](https://accounts.google.com/ServiceLogin?service=cloudconsole&ltmpl=cloud&osid=1&passive=true&continue=https://console.cloud.google.com/appengine?src%3Dac). This is where you will host your repository, store your data, and manage your application.

After this, you will install the [Cloud SDK](https://cloud.google.com/sdk/downloads). Follow the instructions to get set up. I HIGHLY recommend following Google's [Quick Start Guide](https://cloud.google.com/appengine/docs/python/quickstart). This will walk you through the Gcloud process in a well explained, step by step tutorial.

Clone my repository from my [Github Page](https://github.com/YouKnowBagu/blog-project)

From here, you can launch a development server through your shell. First, open a new terminal window. Navigate to the blog-project directory and run the following:

```
~/../blog-project $ dev_appserver.py .
```

Be sure to include the period at the end! This will allow you to make adjustments to the blog's source files without effecting any live version you deploy. If you have followed the tutorial above, you should be all set to deploy the app! From the same blog-project directory, run the following in your terminal:

```
~/../blog-project $ gcloud app deploy --project [YOUR_PROJECT_NAME]
```

That's it! If everything works, you will now have a web app posted for anyone to see!

## Contact

I am happy to share any insights or answer any questions about this code. You can e-mail me at youknowbagu@gmail.com
