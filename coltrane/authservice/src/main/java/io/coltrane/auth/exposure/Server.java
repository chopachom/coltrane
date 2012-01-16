package io.coltrane.auth.exposure;

import io.coltrane.auth.thrift.AuthService;
import javax.annotation.Resource;
import org.apache.log4j.Logger;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TBinaryProtocol.Factory;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TThreadPoolServer;
import org.apache.thrift.server.TThreadPoolServer.Args;
import org.apache.thrift.transport.TServerSocket;
import org.springframework.stereotype.Service;

/**
 * Thrift server implementation
 *
 * @author nik
 */
@Service("thriftServer")
public class Server {
    
    private static final Logger log = Logger.getLogger(Server.class);
    
    @Resource(name = "authService")
    private AuthService.Iface authService;

    public void start() {
        try {
            int port = 7911;
            TServerSocket serverTransport = new TServerSocket(port);
            AuthService.Processor processor = new AuthService.Processor(authService);
            Factory protFactory = new TBinaryProtocol.Factory(true, true);
            
            Args args = new TThreadPoolServer.Args(serverTransport);
            args.processor(processor);
            args.protocolFactory(protFactory);
            TServer server = new TThreadPoolServer(args);
            log.trace("Starting server on port " + port);
            server.serve();
        } catch (TException ex) {
            log.error("ERROR!", ex);
        }
    }
}
