from mongoengine import disconnect,connect

#genero coneccion con la base de datos en el Cluster
def conectarBd():
    disconnect()
    connect('scopingReview',host="mongodb+srv://admin:LccNwXd87QkFzvu@cluster0.w9zqf.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')
    #connect('scopingReview')
    #connect('scopingReview',host="mongodb+srv://jesushidalgo21:39017426@cluster0.uetum.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')