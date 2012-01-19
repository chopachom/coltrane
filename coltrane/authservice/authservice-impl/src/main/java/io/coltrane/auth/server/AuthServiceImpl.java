package io.coltrane.auth.server;

import io.coltrane.auth.service.UserService;
import io.coltrane.auth.thrift.AuthService;
import org.apache.thrift.TException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * AuthService implementation
 * @author nik
 */
@Service("authService")
public class AuthServiceImpl implements AuthService.Iface {
    
    @Autowired
    private UserService userService;

    @Override
    public boolean checkCredentials(String username, String password) throws TException {
        return userService.checkCredentials(username, password);
    }

    @Override
    public boolean canAccessRepo(String username, String repo) throws TException {
        return userService.canAccessRepo(username, repo);
    }
}
