# AutoPDF
 Convenient automatic PDF conversion and organisation (●'◡'●)



With the power of [OfficeToPDF](https://github.com/cognidox/OfficeToPDF) AutoPDF will convert any office related document to `pdf`. ╰(\*°▽°\*)╯ For a complete list, take a look at [here](https://github.com/cognidox/OfficeToPDF#supported-file-types). Works only on **Windows** for now.



## Who needs it?

I myself wrote AutoPDF out of convenience for school. There are always teachers who upload their documents as `docx` and I am tired of opening Word, waiting till it's up and running and then export it to `pdf`, all while the lesson continues. (╯°□°）╯︵ ┻━┻

If you have similar experiences or are able to imagine another use case than for school, work etc, then it is the right tool for you ☜(ﾟヮﾟ☜).



## How it works

- Autonomous installation and updates of the`OfficeToPDf` binary (⌐■_■)
- Creates a replica of the folder structure from a specified root directory
- Opens automatically the `Explorer.exe` for you
- Listens to files being copied / moved into the replica and converts them to `pdf` into the original folder structure
- Windows notifications on important events



## How to get it running

Execute `main.py`:

​	`python main.py`

When prompted, specify the **root directory of your documents**. That's the top most folder, that you want AutoPDF to convert PDF-files to. **Do not** put something like `C:\` in that as all the subdirectories will be replicated and it might crash your computer. 

Next specify the root directory for the temporary replica of the previously specified directory. It really can be anywhere as long as it is empty. If the folder does not exist AutoPDF will create it for you.

AutoPDF will save the configuration so you won't have to configure it on subsequent uses again!

Or import `autopdf` into your Python-script and you'll now what to do :)



## Dependencies

Tested & developed on Python 3.9+.

`requirements.txt`:

```
watchdog
Send2Trash
requests
github3.py
packaging
win10toast_click
```



## Help

If any problems occur, please don't be afraid to create an issue or contact me directly. Any pull request is welcome :)



 ## Future

Much more sophisticated configuration paired with a simple graphical user interface would be amazing to have implemented. ╰(\*°▽°\*)╯

But packaging is more pressing as currently it is unlikely that someone without any Python knowledge is able to install and run AutoPDF ಠ_ಠ.



