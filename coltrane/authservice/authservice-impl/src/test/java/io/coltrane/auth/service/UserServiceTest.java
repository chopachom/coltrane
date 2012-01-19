package io.coltrane.auth.service;

import io.coltrane.auth.domain.User;
import io.coltrane.auth.repository.DomainHelper;
import io.coltrane.auth.repository.UserRepository;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;
import static org.mockito.Mockito.*;

/**
 *
 * @author nik
 */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/spring/UserServiceTest-context.xml")
public class UserServiceTest {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    @Qualifier("userRepositoryMock")
    private UserRepository userRepositoryMock;
    
    @Test
    public void testCheckCredentials() {
        String password = "123456";
        String invalidNickName = "Invalid Nickname";
        User user = DomainHelper.createDeveloper(password);
        
        when(userRepositoryMock.findByNickName(user.getNickName())).thenReturn(user);
        when(userRepositoryMock.findByNickName(invalidNickName)).thenReturn(null);
        
        assertTrue(userService.checkCredentials(user.getNickName(), password));
        assertFalse(userService.checkCredentials(user.getNickName(), password + "5")); // invalid password
        assertFalse(userService.checkCredentials(invalidNickName, password));
        
        verify(userRepositoryMock, times(2)).findByNickName(user.getNickName());
        verify(userRepositoryMock).findByNickName(invalidNickName);
    }
}
