package io.coltrane.auth.service;

/**
 *
 * @author nik
 */
public interface UserService {

    boolean checkCredentials(String userName, String password);
    boolean canAccessRepo(String userName, String repo);
}
