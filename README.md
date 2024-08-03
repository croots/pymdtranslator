
# pymdtranslator

A translation tool (quickly put together) for markdown files written in Python. Currently only supports OpenAI. This uses the batch API to reduce the cost of translation. With GPT-4o-mini and batching, the cost is less than a penny to translate a ~500 English word document to 10 different languagees.

The translation is done in batches as I've noticed GPT-4o starts drop content after a certain point if you just throw a whole document at it.

At this time, this is a quick implementation. Content may be uploaded to OpenAI in a way where it splits things like code blocks (which might result in extra formatting) that could require additional clean up.

This was built in a way to be extensible, so we can add additional providers in the future like self hosted solutions, or Bard.

Its worth checking out [this other project](https://github.com/smikitky/chatgpt-md-translator) which accomplishes the same goal but it A) is more refined B) is written in TypeScript and C) does not use the batch API at time of writing.

Some areas of improvement:

- Add additional providers
- Edit language settings and API keys from CLI
- Better commments and documentation
- "Don't trust the user" sanity checks
- Better handling for things like code blocks

## Installation

Clone this repo, then `pip install ./` from the repo's root directory.

## Usage

In a folder with your markdown files, create a new file called `.languagesettings.json` with the following contents for each language you want to translate to:

```json
{
  "french": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "dialect": "",
    "code": "fr"
  },
  "german" {...
}
```

Create another file called `.keys` containing your OpenAPI key. Don't do the translation in the same folder as where you're hosting your website or you'll leak your API key.

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Then run `pymdtranslator translate <file>` to translate the file.

If your run is inturrupted, you can run `pymdtranslator build <UUID>` to resume from the process of pulling the results and assembling the files.

The output will be new files in the same folder as the input file with the same name but with an additional tag based on the country code (ready to drop into [Zola](https://www.getzola.org/) for example).)
