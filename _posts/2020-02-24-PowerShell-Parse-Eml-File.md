---
title: "PowerShell parse EML files"
excerpt: "Parse EML subjects correctly: folded headers, MIME encoding, a portable Python parser and the original Windows COM workflow."
categories:

  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Functions
last_modified_at: 2026-11-02
---

In the original workflow, I needed to parse an email message saved as an `.eml` file. The surprise was how much a simple subject-line extraction depended on understanding email headers.

To give you some background I implemented a solution sending notifications to a dedicated *Microsoft Teams* channel containing some information that needed to be parsed by a script and eventually take some actions.

I initially thought this would have been rather easy. I was wrong.

## EML is an email message, not a proprietary format

An `.eml` file commonly stores an Internet email message, including headers and a body that may use MIME. The relevant standards include [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322) and [MIME](https://www.rfc-editor.org/rfc/rfc2045). The filename extension is a convention; the format is not an obsolete Microsoft-only encoding.

In the Teams workflow described here, I could retrieve the saved message, but extracting its subject correctly required handling folded headers and encoded text.

## EML as a text file

My requirement was to extract the **subject** line of the message as it contained information I needed and, as EML is just like a regular text file, I initially thought I could easily get away with something similar the following:

```powershell
# Define regex
[string]$subjectRegex = '^subject:'

# Get eml content
$emlFile = Get-Content -Path $pathToEmlFile

# Get only relevant data
$emlFile = $emlFile -match $subjectRegex
```

The above was working while testing the solution in an interactive session but when I started feeding real production data to the script the parsed data was missing key data I knew was in the original eml file (if you're working the subject line contained a *[DO NOT MODIFY]* tag followed by two listing email addresses, so a rather long string).

The subject header was folded across continuation lines. A regex matching only the physical line beginning with `Subject:` misses those continuations; non-ASCII text may also use encoded-word syntax. This is why a message parser is preferable to a line filter.

## Python to the rescue! Or not?

Not being able to find an easy way out of my *issue* via PowerShell I initially thought using Python to parse the eml file as there are libraries for parsing messages. Python also has a standard-library `email` parser; installing a third-party package is not required just to read a subject.

While working this solution was introducing some other challenges and making the whole solution more complicated then I remembered a colleague dealing with this format in C# back at the time so I started scouting Stack Overflow posts [and found this](https://stackoverflow.com/questions/936422/recommendations-on-parsing-eml-files-in-c-sharp/2838544#2838544) which was describing exactly my problem!

### A portable parser option

If Python is available, its standard library handles folded and encoded headers:

```python
from email import policy
from email.parser import BytesParser

with open("message.eml", "rb") as source:
    message = BytesParser(policy=policy.default).parse(source)
subject = str(message["Subject"]) if message["Subject"] is not None else None
```

This returns `None` when the subject is absent. The subject is still untrusted message content: apply the application's own validation before using it to trigger automation. See [email.parser](https://docs.python.org/3/library/email.parser.html).

### Convert-EmlFile: the original Windows implementation

The following is the historical COM-based implementation from my workflow. It depends on Windows and the ADODB/CDO components being registered; it is not a cross-platform PowerShell parser. COM lifetime and error cleanup also need to be handled in a production implementation.


**Convert-EmlFile** is a really simple function which does exactly what is described in the above post, it uses the *ADODB class* to return an object you can easily interact with within PowerShell.

Here's the code:

```powershell
function Convert-EmlFile
{
<#
    .SYNOPSIS
        Function will parse an eml files.

    .DESCRIPTION
        Function will parse eml file and return a normalized object that can be used to extract infromation from the encoded file.

    .PARAMETER EmlFileName
        A string representing the eml file to parse.

    .EXAMPLE
        PS C:\> Convert-EmlFile -EmlFileName 'C:\Test\test.eml'

    .OUTPUTS
        System.Object
#>
    [CmdletBinding()]
    [OutputType([object])]
    param
    (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]
        $EmlFileName
    )

    # Instantiate new ADODB Stream object
    $adoStream = New-Object -ComObject 'ADODB.Stream'

    # Open stream
    $adoStream.Open()

    # Load file
    $adoStream.LoadFromFile($EmlFileName)

    # Instantiate new CDO Message Object
    $cdoMessageObject = New-Object -ComObject 'CDO.Message'

    # Open object and pass stream
    $cdoMessageObject.DataSource.OpenObject($adoStream, '_Stream')

    return $cdoMessageObject
}
```

The function accepts only a single parameter *-EmlFileName* which is a string representing the path, either local or UNC, to the eml file itself, and will return a **formatted** object you can work with.

**Note:** Supply an existing, fully qualified local or UNC path and run with an identity that can read it. A missing file or COM component should be handled as a parsing failure, not as an empty message.
{: .notice--primary}

Here's a sample run and output where I've removed sensitive information:

```powershell
# Define path to the eml file
[string]$emlFile = '\\Server01\Data\Message.eml'

Convert-EmlFile -EmlFileName $emlFile

# Output
BCC                  :
CC                   :
FollowUpTo           :
From                 : "Test recipient" <test@pscustomobject.om>
Keywords             :
MimeFormatted        : True
Newsgroups           :
Organization         :
ReceivedTime         : 2/7/2020 1:56:34 PM
ReplyTo              :
DSNOptions           : 0
SentOn               : 2/7/2020 1:56:30 PM
Subject              : [Test Subject] - A very long subject line for the test 
To                   : "PsCustomObject Test recipient" <test@pscustomobject.com>
TextBody             :
                       Mail text + HTML signature if present

HTMLBody             : <html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"
                       xmlns:w="urn:schemas-microsoft-com:office:word"
                       xmlns:m="http://schemas.microsoft.com/office/2004/12/omml"
                       xmlns="http://www.w3.org/TR/REC-html40">
<snip>
Attachments          : System.__ComObject
Sender               :
Configuration        : System.__ComObject
AutoGenerateTextBody : False
EnvelopeFields       :
TextBodyPart         : System.__ComObject
HTMLBodyPart         : System.__ComObject
BodyPart             : System.__ComObject
DataSource           : System.__ComObject
Fields               : System.__ComObject
MDNRequested         : False
```

As you can see function will parse the file and output an object that is easy to work with for example to extract the subject line or any other part of the text available in the message.

### Function availability

Function is available in my GitHub repository for functions [here](https://github.com/SingularVector/PowerShell-Functions) and will soon be made available in my [IT-ToolBox](https://github.com/SingularVector/IT-ToolBox) module as well.

If you find any issue or have any question do not hesitate to leave me a comment here or open an issue in GitHub.
