# Ministering Views
 Tool for viewing ministering assignments. This tool is not supported or endorsed in any way by the Church of Jesus Christ of Latter-Day Saints.

Instructions:
1. Log in to the LCR using your credentials.
2. Navigate to https://lcr.churchofjesuschrist.org/services/umlu/report/member-list?lang=eng&unitNumber=[your_unit_number_here!]
  (Note: replace "[your unit number here!]" with your ward's unit number, e.g. ...unitNumber=783947)
3. Save the webpage as "member-list.json" in the same directory as ministering_views.py
4. Navigate to https://lcr.churchofjesuschrist.org/ministering?lang=eng&type=EQ
5. Save the webpage with the default name "Ministering Brothers.html"
6. Navigate to https://lcr.churchofjesuschrist.org/ministering?lang=eng&type=RS
7. Save the webpage with the default name "Ministering Sisters.html"
8. Execute the python script "ministering_views.py" (tested with Python 3.6.8)
```
python ministering_views.py
```

Description of generated files found in the "reports" directory:
1. File "ministering-assignments.csv": The household is in the first column. All EQ/RS members ministering to that household are in the subsequent columns.
2. File "ministering-stats-RS.csv": The first column contains a list of the members of the RS. The subsequent columns contain the households/families that are ministered to by the RS member.
3. File "ministering-stats-EQ.csv": The first column contains a list of the members of the EQ. The subsequent columns contain the households/families that are ministered to by the EQ member.

---

MIT License

Copyright (c) 2020 Ben Arnold

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
