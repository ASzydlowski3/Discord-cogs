The MarkovGen is a Python application that generates humorous text-based memes using Markov chains. It can create memes in various styles, including demotivational posters, Paulo Coelho quotes, Gru from "Despicable Me," and comic-style captions.
Features

    Generate text-based memes with different styles.
    Scrape text data from specified channels for use in Markov chains.
    Download and use images from URLs to create demotivational posters.
    Automatically pin generated memes with a certain number of reactions.
	
Usage
Generating Memes

To generate a meme, use the !pykpyk command followed by a subcommand:

    !pykpyk duszenie: Generate a random humorous sentence.
    !pykpyk demot: Create a demotivational poster with random text.
    !pykpyk paulo: Generate a meme with a Paulo Coelho quote.
    !pykpyk gru: Create a meme in the style of Gru from "Despicable Me."
    !pykpyk komix: Generate a comic-style meme with multiple captions.

Scraping Text Data

Use the following commands to scrape text data from specified channels:

    !refresh_messages: Scrapes messages from configured channels and updates the Markov chain text data.
    !refresh_images: Downloads images from configured channels and updates the list of available images.

Automatically Pinning Memes

The application can automatically pin memes that receive a certain number of reactions. This feature helps highlight popular memes in the server.
Configuration

You can configure the behavior of the Markov Meme Generator by editing the script according to the comments.

    List of allowed channels for meme generation.
    Working directory for data storage.
    List of channels to scrape text data from.
    List of channels to scrape images from.
    Path to meme templates.