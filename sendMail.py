import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header



def sendHtmlMail(png_list = []):
    sender = 'axxxxxx@xxxxx.com'
    receivers = ['axxxxxx@xxxxx.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = Header("axxxxxx@xxxxx.com", 'utf-8')
    msgRoot['To'] =  Header("axxxxxx@xxxxx.com", 'utf-8')
    subject = '东太湖论坛关键词监控'
    msgRoot['Subject'] = Header(subject, 'utf-8')
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    mail_msg = """
    <h3>东太湖论坛关键词监控</h3>
    """
    for index,item in enumerate(png_list):
        mail_msg +=f'''
        <p><img src="cid:image{index}"></p>
        '''
        fp = open(item, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', f'<image{index}>')
        msgRoot.attach(msgImage)
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
    try:
        smtpObj = smtplib.SMTP('mail.xxxxx.com',25)
        smtpObj.login('axxxxxx','as*fasdf')
        smtpObj.sendmail(sender, receivers, msgRoot.as_string())
        print ("邮件发送完成")
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")
