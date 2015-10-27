# What is HeatSeeker? #

HeatSeeker is a simple system that can be integrated into your mobile apps, website, desktop games or basically anything. HeatSeeker generates a heat map for any of the above mentioned.


# Cool. So how does it work? #

The procedure used by HeatSeeker is simple. The application or website you are monitoring sends data in the form of x and y coordinates to a server which has Python and ImageMagick installed. The data is then stored in a logfile in the format of x, y. Then the python script available here is configured using the application image, the logfile and a few other parameters. The script is then run to produce the heat map. The heat map is saved as a png file. All done!

# So how do I set it up? #

To set it up please look at the [Setup](Setup.md) page.