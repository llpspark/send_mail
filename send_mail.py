#encoding='utf-8'

import os
import time
import xlrd

from email import encoders
from email.mime.base import MIMEBase
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

def read_file(file_path):
	file_list = []
	work_book = xlrd.open_workbook(file_path)
	sheet_data = work_book.sheet_by_name('Sheet1')
	print('now is process :', sheet_data.name)
	Nrows = sheet_data.nrows
	
	for i in range(1, Nrows):
		file_list.append(sheet_data.row_values(i))

	return file_list


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


'''加密发送文本邮件'''
def sendEmail(from_addr, password, smtp_server, img_dir, file_list, log_path):
	#server = smtplib.SMTP(smtp_server,80)
	server = smtplib.SMTP_SSL(smtp_server,465)#使用465端口
	#server.set_debuglevel(1) # 记录详细信息
	server.login(from_addr, password) # 登录邮箱服务器
	
	with open(log_path, 'w+', encoding='utf-8') as f_w:
		for i in range(len(file_list)):
			try:
				person_info = file_list[i]
				order_num, person_name, card_number, card_password, email_add = str(person_info[0]), str(person_info[1]), \
				str(person_info[2]), str(person_info[3]), str(person_info[4])
				if "." in card_number:
					card_number = card_number.split(".")[0]
				if "." in card_password:
					card_password = card_password.split(".")[0]

				html_content = \
				'''
				<html>
				<body>
					<h3 align="center">2019年春节过节费发放通知</h3>
					<p> <div face="Verdana" align="center">***公司（XZ）字第20190201号</div></p>
					<p>您好：</p>
					<blockquote><p>2019年春节，为答谢您对公司的辛勤付出，特为您送上节日贺礼一张，请查收！</p></blockquote>
					
					<blockquote><p><strong>京东E卡，价值￥300.00元。</strong></p></blockquote>
					<blockquote><p><strong>以下信息自左依次为：姓名、卡号、密码</strong></p></blockquote>
					<blockquote><p><strong>{name_info}   {card_number_info}   {card_password_info}</strong></p></blockquote>

					<blockquote><p>请您收到卡密后，尽快登陆京东账号进行绑定，并在卡有效期2022年01月14日前消费使用，以免造成信息泄露和不必要的损失。</p></blockquote>
					<blockquote><p>预祝您节日快乐！</p><blockquote>


					<p align="right">***公司文化建设委员会</p>  
					<p align="right">2019年2月1日</p> 


					【充值方法】
					<p><img src="cid:1"></p>
					<p><img src="cid:2"></p>
					<p><img src="cid:3"></p>
					<p><img src="cid:4"></p>
					<p><img src="cid:5"></p>


				</body>
				</html>
				'''.format(name_info = person_name, card_number_info = card_number, card_password_info = card_password)


				#msg = MIMEText(text_content, 'html', 'utf-8') # html邮件
				msg = MIMEMultipart()
				msg.attach(MIMEText(html_content, 'html', 'utf-8'))
				i = 1
				for img_file in os.listdir(img_dir):
					with open(os.path.join(img_dir + img_file), 'rb') as im:
						# 设置附件的MIME和文件名，这里是png类型:
						mime = MIMEBase('image', 'png', filename=img_file)
						# 加上必要的头信息:
						mime.add_header('Content-Disposition', 'attachment', filename=img_file)
						mime.add_header('Content-ID', '<%i>' %i)
						#mime.add_header('X-Attachment-Id', 'img_file')
						# 把附件的内容读进来:
						mime.set_payload(im.read())
						# 用Base64编码:
						encoders.encode_base64(mime)
						# 添加到MIMEMultipart:
						msg.attach(mime)
						i = i + 1

				msg['From'] = _format_addr('**公司文化建设委员会 <%s>' % from_addr)
				msg['To'] = _format_addr(person_name + '<%s>' % email_add)
				msg['Subject'] = Header('2019年春节过节费发放通知', 'utf-8').encode()
				
				#time.sleep(20)
				server.sendmail(from_addr, [email_add], msg.as_string()) # 发送信息

				log_i = str("序号："+ str(order_num) + "  姓名：" +  person_name  +  "已发送成功！")
				print(log_i)
				f_w.write(log_i)
				f_w.write('\r\n')
				
			except smtplib.SMTPConnectError as e:
				print('邮件发送失败，连接失败:', e.smtp_code, e.smtp_error)
			except smtplib.SMTPAuthenticationError as e:
				print('邮件发送失败，认证错误:', e.smtp_code, e.smtp_error)
			except smtplib.SMTPSenderRefused as e:
				print('邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error)
			except smtplib.SMTPRecipientsRefused as e:
				print('邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error)
			except smtplib.SMTPDataError as e:
				print('邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error)
			except smtplib.SMTPException as e:
				print('邮件发送失败, ', e.message)
			except Exception as e:
				print("发送失败" + e)
	server.quit()




if __name__ == '__main__':

    root_dir = 'D:\\related_files\\grocery'
    file_path = root_dir + "\\zyy.xlsx"
    log_path = root_dir + "\\log_file.txt"
    img_dir = root_dir + "\\imgs\\" 
    from_addr = '***@***.cn'   # 邮箱登录用户名
    password  = '***'           # 登录密码
    smtp_server='smtp.mxhichina.com'     # 阿里服务器地址，默认端口号25

    file_list = read_file(file_path)
    sendEmail(from_addr, password, smtp_server, img_dir, file_list, log_path)
    print('ok')



