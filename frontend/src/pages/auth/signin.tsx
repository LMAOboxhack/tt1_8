import {
  Box,
  Button,
  Card,
  CardBody,
  Flex,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  Heading,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  Link,
  Stack
} from '@chakra-ui/react';
import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { FaLock, FaUserAlt } from "react-icons/fa";

type IFormInputs = {
  username: string;
  password: string;
};

export default function SignIn() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<IFormInputs>();

  const [showPassword, setShowPassword] = useState(false);

  const handleShowClick = () => setShowPassword(!showPassword);

  const onSubmit = async (data: IFormInputs) => {
    const res = await signIn('credentials', {
      username: data.username,
      password: data.password,
      callbackUrl: '/dashboard',
      redirect: false,
    });

    if (res?.status !== 200) {
      alert('Username or password incorrect. Please try again.');
    } else {
      window.location.href = '/';
    }
  }

  return (
    <Flex
      flexDirection="column"
      width="100wh"
      height="100vh"
      backgroundColor="gray.200"
      justifyContent="center"
      alignItems="center"
    >
      <Stack
        flexDir="column"
        mb="2"
        justifyContent="center"
        alignItems="center"
      >
        <Heading color="teal.400">Welcome!</Heading>
        <Card minW={{ base: "90%", md: "468px" }} my={3}>
          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack
                spacing={4}
                p="1rem"
              >
                <FormControl isInvalid={errors.username === null}>
                  <InputGroup>
                    <InputLeftElement
                      pointerEvents="none"
                    >
                      <FaUserAlt color="gray.300" />
                    </InputLeftElement>
                    <Input type="text" placeholder="Username" {...register('username')} />
                  </InputGroup>
                  <FormErrorMessage>
                    {errors.username && errors.username.message?.toString()}
                  </FormErrorMessage>
                </FormControl>
                <FormControl isInvalid={errors.password === null}>
                  <InputGroup>
                    <InputLeftElement
                      pointerEvents="none"
                      color="gray.300"
                    >
                      <FaLock color="gray.300" />
                    </InputLeftElement>
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Password"
                      {...register('password')}
                    />
                    <InputRightElement width="4.5rem">
                      <Button h="1.75rem" size="sm" onClick={handleShowClick}>
                        {showPassword ? "Hide" : "Show"}
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                  <FormHelperText textAlign="right">
                    <Link>Forgot password?</Link>
                  </FormHelperText>
                  <FormErrorMessage>
                    {errors.password && errors.password.message?.toString()}
                  </FormErrorMessage>
                </FormControl>
                <Button type="submit">
                  Login
                </Button>
              </Stack>
            </form>
          </CardBody>
        </Card>
      </Stack>
      <Box>
        New to us?{" "}
        <Link color="teal.500" href='/auth/register'>
          Sign Up
        </Link>
      </Box>
    </Flex>
  )
}