# bbr4
This is the source code for the BrassBandResults.co.uk project.  This version is for deployment onto the AWS platform.

## Platform
Amazon Web Services
* S3 for file uploads and static media
* RDS (PostgreSQL with PostGIS) for data storage
* EC2 instance for web server tier
    * Python 3
    * Django
    * nginx
    * Gunicorn
* SNS for change notification
* Lambda for thumbnailing

## Documentation
The development wiki for this project contains more information, see https://github.com/BrassBandResults/bbr4/wiki