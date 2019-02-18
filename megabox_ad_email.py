import mail_client


def email_ad():

	#this is the banner ad for the pool

    rules = """
    <html>

    <head>
    </head>

    <body>
    <div style="font-family: Verdana;">
    <br>
    <span style="font-size:18px; color:#000000;">Join the MegaBox March Madness Pool!</span>
    <br>
    <br>
    <div class="rules" style="border: 2px solid; background-color: #f2f2f2;padding:10px;width:1000px; font-family: Lucida Sans; font-size:16px; color:#000000;">
    <div class="rule_header" style="position:absolute; top:90px; left: 350px; font-size:18px; color:#000000;"><strong>Rules of the Game</strong></div>
    <ol>
    <br>
    <li>The game works like a standard "Football Box" Pool. &nbsp;Each player buys a box (Entry Fee = 100 per box) in a 10-by-10 grid.</li><br>
    <li>Each box in the grid represents the intersection of the last digits of the final score for each tournament game.</li><br>
    <li>The digits across the TOP of the grid represent the last digit in the final score from THE FAVORITE (The Higher Team Seed).</li><br>
    <li>The digits across the SIDE of the grid represent the last digit in the final score from THE UNDERDOG (The Lower Team Seed).</li><br>
    <li>The digits for the game grid will be drawn the Wednesday evening prior to start of the tournament.</li><br>
    <li>Your box numbers apply for EVERY game in the tournament.<br><br><strong>Whenever ANY tournament game's final score lands on your box - YOU WIN!</strong></li><br>
    </ol>
   
    
    <div>
    <br>
    <span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>Payouts Per Game --- By Round</strong></span> 
    <br> <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 1 (Opening Round - 32 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            50 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 2 (16 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            100 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 3 (Sweet Sixteen - 8 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            200 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 4 (Quarter Finals - 4 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            400 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 5 (Final Four - 2 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            800 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 6 (NCAA Final)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            2000 pts
        </td>
      </tr>
    </table>
    <br>
    <br>
    </div>

    </div>
    <br>
    <span style="font-size:18px; color:#000000;">Go Choose Your Box At The Weblink Below!<br>Good Luck!</span>
    <br>
    <br>
    <a href="http://www.megaboxhoops.com/" style="font-size: 20px; text-decoration: none">March Madness MegaBox Pool</a>
    </div>

    </body>
    </html>
    """

    subject = "Join to The MegaBox March Madness Pool"
    mail_client.mail('megaboxhoops@gmail.com',subject,text='',html=rules)



if __name__ == "__main__":
	email_ad()
