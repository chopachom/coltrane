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
    public boolean isHaveAccessToRepo(String userName, String appDomain) throws TException {
        throw new UnsupportedOperationException("Not supported yet.");
    }
}
