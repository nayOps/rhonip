import { GetServerSideProps } from 'next'

export const getServerSideProps: GetServerSideProps = async () => {
  return {
    redirect: {
      destination: '/enrollment',
      permanent: false,
    },
  }
}

export default function Index() {
  return null
}




