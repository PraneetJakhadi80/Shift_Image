USE [Camera_Data]
GO
/****** Object:  Table [dbo].[camera_detail]    Script Date: 6/28/2023 4:10:44 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[camera_detail](
	[ip_address] [nvarchar](50) NULL,
	[username] [varchar](50) NULL,
	[password] [varchar](50) NULL,
	[rtsp_port] [bigint] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[email_config]    Script Date: 6/28/2023 4:10:45 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[email_config](
	[smtp_host] [varchar](50) NULL,
	[smtp_port] [int] NULL,
	[sender_email] [varchar](50) NULL,
	[sender_password] [varchar](50) NULL,
	[receiver_email] [varchar](50) NULL,
	[cc_emails] [varchar](100) NULL
) ON [PRIMARY]
GO
INSERT [dbo].[camera_detail] ([ip_address], [username], [password], [rtsp_port]) VALUES (N'192.168.1.64', N'admin', N'password@123', 554)
INSERT [dbo].[camera_detail] ([ip_address], [username], [password], [rtsp_port]) VALUES (N'192.168.1.65', N'admin', N'password@123', 554)
GO
INSERT [dbo].[email_config] ([smtp_host], [smtp_port], [sender_email], [sender_password], [receiver_email], [cc_emails]) VALUES (N'smtp.gmail.com', 587, N'senders_email', N'senders_password', N'receivers_mail', N'cc_1_mail, cc_2_mail ')
GO
