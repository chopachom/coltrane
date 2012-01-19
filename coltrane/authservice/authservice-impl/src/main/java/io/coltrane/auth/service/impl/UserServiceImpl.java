package io.coltrane.auth.service.impl;

import io.coltrane.auth.domain.User;
import io.coltrane.auth.repository.ApplicationRepository;
import io.coltrane.auth.repository.UserRepository;
import io.coltrane.auth.service.UserService;
import org.mindrot.jbcrypt.BCrypt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 *
 * @author nik
 */
@Service("userService")
public class UserServiceImpl implements UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private ApplicationRepository appRepository;

    @Override
    @Transactional(readOnly = true)
    public boolean checkCredentials(String userName, String password) {
        if (userName == null || password == null || userName.isEmpty() || password.isEmpty()) {
            // throw exception
        }
        User user = userRepository.findByNickName(userName);
        if (user == null) {
            return false;
        }
        return BCrypt.checkpw(password, user.getPasswordHash());
    }

    @Override
    @Transactional(readOnly = true)
    public boolean canAccessRepo(String userName, String repo) {
        if (userName == null || repo == null || userName.isEmpty() || repo.isEmpty()) {
            // throw exception
        }
        return appRepository.findByAuthorAndAppDomain(userName, repo) != null;
    }
}
