# Transform Insightly form fields
For exact functionality, read the Python script in the repo.

## Installation as Hostpoint Cron job
1. Copy `insigthly_transform_fields.py` to your hostpoint server, e.g. into the `bin` folder. The path then looks like this: `/home/<servername>/bin/insigthly_transform_fields.py`.
2. Make sure the file is executable (`chmod +x ...`)
3. Set your `API_KEY` and `ISPROCESSED_FIELD_ID` in the script
4. Go to the cronjob manager (`Advanced > Cronjob Manager`)
5. Set `it@entrepreneur-club.org` as *E-Mail address*
6. Add a new job
7. Set `m`: `0,15,30,45`, `h`: `*`, `M.day`: `*`, `Month`: `*`, `W.day`: `*`, `Command`: `/home/<servername>/bin/insigthly_transform_fields.py`

Thats it!

## Form

Find a sample form in `example_form.html`.
