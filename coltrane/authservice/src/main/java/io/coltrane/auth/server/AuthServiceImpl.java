package io.coltrane.auth.server;

import io.coltrane.auth.thrift.AuthService;
import org.apache.thrift.TException;
import org.springframework.stereotype.Service;

/**
 * AuthService implementation
 * @author nik
 */
@Service("authService")
public class AuthServiceImpl implements AuthService.Iface {

    @Override
    public boolean checkCredentials(String username, String password) throws TException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean canAccessRepo(String username, String repo) throws TException {
        throw new UnsupportedOperationException("Not supported yet.");
    }
}
