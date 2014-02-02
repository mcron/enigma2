#ifndef __DVB_STREAMSERVER_H_
#define __DVB_STREAMSERVER_H_

#include <vector>

#include <lib/network/serversocket.h>
#include <lib/service/servicedvbstream.h>

class eStreamServer;

class eStreamClient: public eDVBServiceStream
{
protected:
	eStreamServer *parent;
	int streamFd;

	bool running;

	void notifier(int);
	ePtr<eSocketNotifier> rsn;

	std::string request;

	void streamStopped();
	void tuneFailed();

public:
	eStreamClient(eStreamServer *handler, int socket);
	~eStreamClient();

	void start();
};

class eStreamServer: public eServerSocket
{
	DECLARE_REF(eStreamServer);

	eSmartPtrList<eStreamClient> clients;

	void newConnection(int socket);

public:
	eStreamServer();
	~eStreamServer();

	void connectionLost(eStreamClient *client);
};

#endif /* __DVB_STREAMSERVER_H_ */
