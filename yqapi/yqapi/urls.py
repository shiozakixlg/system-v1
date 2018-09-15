"""yqapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from yqdata import views, views_topics, views_realtime_monitor, views_dashboard, views_settings, views_senmassage, views_hot_topic, views_search, views_retrieval, views_sen_topic,views_users,views_translate, views_usermessage, views_login, es_test, views_pull, views_pull_socket, views_knownledge
from websocketdata import views_socket

urlpatterns = [
        #url(r'^admin/', include(admin.site.urls)),
    url(r'^yqdata/search$', views_search.Search.as_view()),
    url(r'^yqdata/dashboard$', views_dashboard.dashboard_sourceData),
    url(r'^yqdata/dashboard_time$', views_dashboard.dashboard_sourceData_time),
    url(r'^yqdata/topic_statistics$', views_topics.Topic_statistics.as_view()),
    url(r'^yqdata/topic_analysis$', views_topics.Topic_analysis.as_view()),
    url(r'^yqdata/hot_topic_analysis$', views_hot_topic.Hot_Topic_analysis.as_view()),
    url(r'^yqdata/monitor/all$', views_realtime_monitor.RealtimeMonitorAll.as_view()),
    url(r'^yqdata/monitor/group$', views_realtime_monitor.RealtimeMonitorGroup.as_view()),
    url(r'^yqdata/monitor/flush$', views_realtime_monitor.RealtimeMonitorFlush.as_view()),
    url(r'^yqdata/monitor/load$', views_realtime_monitor.RealtimeMonitorLoad.as_view()),
    url(r'^yqdata/settopic$', views_settings.SetTopic.as_view()),
    url(r'^yqdata/addtopic$', views_settings.addTopic.as_view()),
    url(r'^yqdata/deletetopicother$', views_settings.deleteTopicOther.as_view()),
    url(r'^yqdata/adminmanagetopic$', views_settings.adminManageTopic.as_view()),
    url(r'^yqdata/dataSourceTree$', views_settings.dataSourceTree.as_view()),
    url(r'^yqdata/modifytopic$',views_settings.modifyTopic.as_view()),
    url(r'^yqdata/deletetopic$',views_settings.DeleteTopic.as_view()),
    url(r'^yqdata/batchsetui$',views_settings.batchSettingTopicUI.as_view()),
    # url(r'^yqdata/batchset$',views_settings.batchSettingTopic.as_view()),
    url(r'^yqdata/senmassage/addui$',views_senmassage.addSenmsg_UI.as_view()),
    url(r'^yqdata/senmassage/showrawmsg$',views_senmassage.showRawMsg.as_view()),
    url(r'^yqdata/senmassage/addmsg$',views_senmassage.addSenmsg_add.as_view()),
    url(r'^yqdata/senmassage/showmsg$',views_senmassage.showSenMsg.as_view()),
    url(r'^yqdata/senmassage/delmesg$',views_senmassage.Mesg_delete.as_view()),
    url(r'^yqdata/senmassage/markmesg$',views_senmassage.Mesg_mark_report.as_view()),
    url(r'^yqdata/senmassage/handlemesg$',views_senmassage.Mesg_mark_handle.as_view()),
    url(r'^yqdata/senmassage/senmsgout$',views_senmassage.SenMsgOut.as_view()),
    url(r'^yqdata/senmassage/evidence$',views_senmassage.Evidence.as_view()),
    url(r'^yqdata/retrieval$',views_retrieval.Advanced_Retrieval.as_view()),
    url(r'^yqdata/hot_topic$',views_hot_topic.hotTopic.as_view()),
    url(r'^yqdata/wallpost$',views_sen_topic.wallPost.as_view()),
    url(r'^yqdata/sen_topic$',views_sen_topic.senTopic.as_view()),
    url(r'^yqdata/user_analysis$',views_users.UserAnalysis.as_view()),
    url(r'^yqdata/translate$',views_translate.Translate.as_view()),
    url(r'^yqdata/sen_hot$',views_sen_topic.senHot.as_view()),
    url(r'^yqdata/log_in$',views_login.login.as_view()),
    url(r'^yqdata/user_attr$',views_users.attrUser.as_view()),
    url(r'^yqdata/send_user_msg$',views_usermessage.userMessageSend.as_view()),
    url(r'^yqdata/isread$',views_usermessage.isRead.as_view()),
    url(r'^yqdata/pushmsg$',views_usermessage.pushMsg.as_view()),
    url(r'^yqdata/delusermsg$',views_usermessage.delUserMsg.as_view()),
    url(r'^yqdata/showmsgdetail$',views_usermessage.showMsgDetail.as_view()),
    url(r'^yqdata/showuserlist$',views_users.showUserList.as_view()),
    url(r'^yqdata/send_user_msg_ui$',views_usermessage.userMessageSendUI.as_view()),
    url(r'^yqdata/notreadlist$',views_usermessage.notReadList.as_view()),
    url(r'^yqdata/unreadnum$',views_usermessage.unReadNum.as_view()),
    url(r'^yqdata/watch_user_attr$',views_users.watchAttrUser.as_view()),
    url(r'^yqdata/batchsettopic$',views_settings.batchSettingTopic.as_view()),
    url(r'^yqdata/usersignupui$',views_users.userSignUpUI.as_view()),
    url(r'^yqdata/usersignup$',views_users.userSignUp.as_view()),
    url(r'^yqdata/groupmessage$',views_users.groupMessage.as_view()),
    url(r'^yqdata/modifyuserinfo$',views_users.modifyUserInfo.as_view()),
    url(r'^yqdata/deleteuser$',views_users.deleteUser.as_view()),
    url(r'^yqdata/addgroup$',views_users.addGroup.as_view()),
    url(r'^yqdata/coursetest$',views_hot_topic.courseTest.as_view()),
    url(r'^yqdata/esearch$',es_test.Esearch.as_view()),
    url(r'^yqdata/esort$',es_test.Esort.as_view()),
    url(r'^yqdata/recordin$',es_test.Record_In.as_view()),
    url(r'^yqdata/recordout$',es_test.Record_Out.as_view()),
    url(r'^websocketdata/pull_post$',views_socket.PullPost),
    url(r'^yqdata/pull_table$',views_pull_socket.PullTable.as_view()),
    url(r'^yqdata/hot_value_evolution$',views_knownledge.Hot_Value_Evolution.as_view()),
    url(r'^yqdata/hot_topic_evolution$',views_knownledge.Hot_Topic_Evolution.as_view()),
    url(r'^yqdata/community_detection$',views_knownledge.Community_Detection.as_view()),
    url(r'^yqdata/event_detail$',views_knownledge.Event_Detail.as_view()),
    url(r'^yqdata/opinion_mining$',views_knownledge.Opinion_Mining.as_view()),
    url(r'^yqdata/emotion_analysis$',views_knownledge.Emotion_Analysis.as_view()),
    url(r'^yqdata/score_save$',views_knownledge.Score_Save.as_view()),
    url(r'^yqdata/score_search$',views_knownledge.Score_Search.as_view()),
    url(r'^yqdata/strategy_save$',views_knownledge.Strategy_Save.as_view()),
    url(r'^yqdata/strategy_search$',views_knownledge.Strategy_Search.as_view()),
    # url(r'^yqdata/senmsgoutput$',views_senmassage.SenMsgOutPut.as_view()),)
]
