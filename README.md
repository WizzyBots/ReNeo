# ReNeo

Yet another bot

## What is this

This is the rewrite of my old bot, I eventually lost interest and abandoned it, I now converted this into a suite for other devs to fork
and make their own text commands (cause slash commands don't feel right)

## Config

The basic config needed are all in environment variables/`.env`

the `.env` file has the following options
```
STATIC=<The relative/absolute url to the static file server/route>
TOKEN=<The bot token>
DATABASE_URL=<The postgresql database url for prefixes>
```
`STATIC` and `DATABASE_URL` are optional
`TOKEN` can either be provided by the command line or environment variables

So, go fork this and do what you want, happy development!

## Features

 - A basic one page static site
 - Levenshtein command typo suggestions
 - Sleek embed design
 - Powerful cog and command management system
 - A webhook logging facility (needs to be enabled in code)